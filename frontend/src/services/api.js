const API_BASE_URL = 'http://localhost:8000/api';

export async function getTeams(){
    const response = await fetch(`${API_BASE_URL}/teams/`)

    if(!response.ok){
        throw new Error("Could not load teams");
    }

    return response.json();
}