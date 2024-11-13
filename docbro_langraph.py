from langchain import PromptTemplate, LLMChain
from utils import get_llm

import os, json

# Initialize the language model
llm = get_llm()

# Initialize a global dependency map
dependency_map = {
    "classes": {},       # To store class details (class_name -> file_path, methods, base classes)
    "functions": {},     # To store function details (function_name -> file_path, params)
    "database_tables": {}  # To store database tables if applicable
}


# Function to extract entities from a file and update the dependency map
def extract_entities(file_path, code, dependency_map):
    # Prompt to extract entities
    entity_prompt = PromptTemplate(
        input_variables=["code"],
        template="""
        Analyze the following code. Extract:
        - Classes and their inheritance relations.
        - Functions and their parameters.
        - Database tables (if any).

        Must Return your response in JSON format.

        Code:
        {code}
        """
    )
    llm_chain = LLMChain(llm=llm, prompt=entity_prompt)
    entity_info = llm_chain.run(code=code)

    # print("-------------",entity_info)

    # Try to parse the response as a JSON-like structure
    try:
        try:
            # Convert response to dictionary if JSON format
            entity_info = json.loads(entity_info.strip("```json ")) # Only use eval() if you're sure the format is safe
        except:
            entity_info = eval(entity_info.strip("```json "))

        # print(type(entity_info))
        for entity in entity_info.get("classes", []):
            # print('loooooooooooop')
            class_name = entity["name"]
            dependency_map["classes"][class_name] = {
                "file_path": file_path,
                "base_classes": entity.get("base_classes", []),
                "methods": entity.get("methods", [])
            }

        for func in entity_info.get("functions", []):
            func_name = func["name"]
            dependency_map["functions"][func_name] = {
                "file_path": file_path,
                "parameters": func.get("parameters", [])
            }

        for table in entity_info.get("database_tables", []):
            table_name = table["name"]
            dependency_map["database_tables"][table_name] = {
                "file_path": file_path,
                "columns": table.get("columns", []),
                "relations": table.get("relations", []),

            }

    except Exception as e:
        print(f"Error parsing LLM response for file {file_path}: {e}")
        # Optionally, handle parsing issues or use regex to extract information
    
    return dependency_map

# Analyze repository and update dependency map
def analyze_repository(repo_path):

    # Prompt template for code explanation
    explanation_prompt = PromptTemplate(
        input_variables=["code"],
        template="""
        Explain the following code with focus on its functionality, structure, and relationships:
        {code}
        """
    )

    llm_chain = LLMChain(llm=llm, prompt=explanation_prompt)
    explanations = {}

    for root, _, files in os.walk(repo_path):
        for file_name in files:
            if file_name.endswith((".py", ".js", ".java", ".sql")):  # Filter for code files
                file_path = os.path.join(root, file_name)
                with open(file_path, "r") as file:
                    code = file.read()
                
                # Get explanation and update dependency map
                explanation = llm_chain.run(code=code)
                explanations[file_path] = explanation
                extract_entities(file_path, code, dependency_map)  # Update dependency map
                # break
    return explanations


# Link dependencies across files to determine inheritance and other relations
def link_cross_file_references(dependency_map):
    relationships = []

    for class_name, class_info in dependency_map["classes"].items():
        # Check if base classes refer to other files
        for base_class in class_info["base_classes"]:
            if base_class in dependency_map["classes"]:
                base_class_info = dependency_map["classes"][base_class]
                relationships.append({
                    "class": class_name,
                    "inherits_from": base_class,
                    "defined_in": class_info["file_path"],
                    "inherited_from_file": base_class_info["file_path"]
                })

    return relationships



# Enhanced architectural overview prompt
overview_prompt = PromptTemplate(
    input_variables=["dependency_map", "relationships"],
    template="""
    Based on the following dependency map and relationships, provide a detailed architectural overview of the project.
    
    Include:
    - The roles and responsibilities of each major component (backend, frontend, and database).
    - How the frontend, backend, and database components are interconnected.
    - Class inheritance and function dependencies across files.
    - Database tables and how they're accessed by backend components.
    - Any known architectural patterns (e.g., MVC, microservices) based on the code structure.
    - A summary of data flow within the project, from data ingestion to processing and output.
    
    Dependency Map:
    {dependency_map}

    Relationships:
    {relationships}
    """
)

# Function to generate the architecture overview
def generate_architecture_overview(dependency_map, relationships):
    llm_chain = LLMChain(llm=llm, prompt=overview_prompt)
    overview = llm_chain.run(dependency_map=str(dependency_map), relationships=str(relationships))
    return overview



# Complete code to analyze the repository, link dependencies, and generate overview
repo_path = "./DocBro"  # Specify your repository path here
# repo_path = "./repos\Sphere\PTC\src\main\java\com\systemsltd\profiletracking\controller"

# Step 1: Analyze repository and build dependency map
explanations = analyze_repository(repo_path)

# print(explanations)
print("dependency_map--->>>>>>>>>: ",dependency_map)

# Step 2: Link cross-file references in dependency_map
relationships = link_cross_file_references(dependency_map)

print("relationships--->>>>>>>>>: ",relationships)
# Step 3: Generate the final architectural overview
overview = generate_architecture_overview(dependency_map, relationships)

# Display the final project overview
print("Project Overview:")
print(overview)
