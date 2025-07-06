functions = [
    {
        "name": "get_weather_forecast",
        "description": "Get weather information up to 5 hours in the future using a weather API in a given location. Also this can get current weather information.\
            조금 후의, 혹은 나중의, 이따가, 몇 시간 뒤 등의 날씨 정보가 필요할 때에는 이 함수를 사용해야 한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or dong, e.g. Seoul, Gangnam",
                },
            },
            "required": ["location"],
        },
    },
    {
        "name": "retrieval",
        "description": "Use a retriever to get information from a vectorstore. \
            딸기, 딸기 품종, 해충, 작물관리 등, 딸기 농업에 관한 정보가 필요할 경우에 해당 함수를 사용해야 한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to retrieve information for.",
                },
            },
            "required": ["query"],
        },
    }
]
