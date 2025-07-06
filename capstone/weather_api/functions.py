functions = [
    {
        "name": "get_weather_forecast",
        "description": "Get weather informations up to 5 hours in the future using an weather API in a given location. Also this can get a current weather information.\
            조금 후의, 혹은 나중의, 이따가, 몇 시간 뒤 등의 날씨 정보가 필요할 때에는 이 함수를 사용해야 한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city or dong, e.g. 전주, 금암1동",
                },
            },
            "required": ["location"],
        },
    },
    
    {
        "name": "retrieval",
        "description": "Use a retriever to get information from a vectorstore. \
            딸기 농업, 해충, 작물관리에 관한 정보가 필요할 경우에 해당 함수를 사용해야 한다.",
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

# if chain.invoke -> output(function이 필요한가 ? [auto] elif retrieval이 필요한가? else: general response)