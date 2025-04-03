from typing import List, Any
from py_writes_ts.class_to_interface import generate_typescript_interfaces, ts_name
from py_writes_ts.function_generator import generate_typescript_function
from dataclasses import dataclass


@dataclass
class GetUserByIdRequest:
    id: int

@dataclass
class GetUserByIdResponse:
    id: int
    name: str
    age: int

@dataclass
class GetAllUsersRequest:
    pass

@dataclass
class GetAllUsersResponse:
    users: list[GetUserByIdResponse]

def generate_endpoint_function(name: str, endpoint: str, request_type: Any, response_type: Any, valid_refs: List[Any]):
    function_body = f"""
const response = await fetch(`/api/{endpoint}`, {{
    method: "POST",
    headers: {{
        "Content-Type": "application/json"
    }},
    body: JSON.stringify(params)
}});

if (!response.ok) {{
    throw new Error(`API call failed with status ${{response.status}}`);
}}

const data: {ts_name(response_type)} = await response.json();
return data;
"""

    ts_code = generate_typescript_function(
        function_name=name,
        parameters={
            "params": request_type
        },
        return_type=f"Promise<{ts_name(response_type)}>",
        body=function_body,
        is_async=True,
        valid_refs=valid_refs
    )

    return ts_code

def test_sdk_generator_example() -> None:
    models = [GetUserByIdRequest, GetUserByIdResponse, GetAllUsersRequest, GetAllUsersResponse]

    code = ""
    code += generate_typescript_interfaces(models)
    code += generate_endpoint_function(
        name="getUserById",
        endpoint="get_user_by_id",
        request_type=GetUserByIdRequest,
        response_type=GetUserByIdResponse,
        valid_refs=models,
    )
    code += generate_endpoint_function(
        name="getAllusers",
        endpoint="get_users",
        request_type=GetAllUsersRequest,
        response_type=GetAllUsersResponse,
        valid_refs=models,
    )
    assert code == """export interface GetUserByIdRequest {
    id: number;
}

export interface GetUserByIdResponse {
    id: number;
    name: string;
    age: number;
}

export interface GetAllUsersRequest {
}

export interface GetAllUsersResponse {
    users: GetUserByIdResponse[];
}
export async function getUserById(
    params: GetUserByIdRequest
): Promise<GetUserByIdResponse> {
    const response = await fetch(`/api/get_user_by_id`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    
    if (!response.ok) {
        throw new Error(`API call failed with status ${response.status}`);
    }
    
    const data: GetUserByIdResponse = await response.json();
    return data;
}

export async function getAllusers(
    params: GetAllUsersRequest
): Promise<GetAllUsersResponse> {
    const response = await fetch(`/api/get_users`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
    });
    
    if (!response.ok) {
        throw new Error(`API call failed with status ${response.status}`);
    }
    
    const data: GetAllUsersResponse = await response.json();
    return data;
}

"""
    