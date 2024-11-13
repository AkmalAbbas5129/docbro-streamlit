from langchain.document_loaders import TextLoader
from langchain.schema import Document
import os
import json
from langchain_openai import AzureChatOpenAI, AzureOpenAI
from langsmith import traceable
from utils import get_llm


# Function to generate summary and update JSON with dynamic prompt template
def process_file(current_file_content, previous_summary, json_template, llm_model, prompt_template):
    # Format the dynamic prompt using the provided template
    prompt = prompt_template.format(
        current_file_content=current_file_content,
        previous_summary=previous_summary,
        json_template=json.dumps(json_template, indent=4)
    )
    

    # Run the OpenAI model
    response = llm_model(prompt)
    
    # Extract the actual text from the response (AIMessage content)
    response_content = response.content

    return response_content

def make_batches(file_list, batch_size):
    """
    Splits the list of file paths into batches of a specified size.

    :param file_list: List of file paths.
    :param batch_size: The number of files to include in each batch.
    :return: A list of batches, where each batch is a list of file paths.
    """
    batches = [file_list[i:i + batch_size] for i in range(0, len(file_list), batch_size)]
    return batches

def load_documents_list(files_batch):
    batch_document = ""
    unsupported_docs = []
    for i, file_path in enumerate(files_batch):
        try:
            # Load the document using Langchain's TextLoader
            loader = TextLoader(file_path)
            documents = loader.load()

            # Assuming a single document is loaded
            document = documents[0]  # Extract the first (and likely only) document
            
            batch_document += "\n\n---------------------------------------------\n\n"+str(document)
        except:
            unsupported_docs.append(file_path)
        
    return batch_document, unsupported_docs
        
# Main loop to iterate over files
def process_files(file_list, json_template, llm, prompt_template):
    
    batch_size = 15
    files_batches = make_batches(file_list, batch_size)
    
    unsupported_docs_ = []
    summary = ""
    for i, files_batch in enumerate(files_batches):
        try:
            batch_document, unsupported_docs = load_documents_list(files_batch)
            unsupported_docs_.extend(unsupported_docs)
            # print(f"\nProcessing batch {i + 1}/{len(files_batches)}: {files_batch}\n\n")

            # Update the JSON template and get a summary for each file
            summary = process_file(batch_document, summary, json_template, llm, prompt_template)
        except Exception as e:
            # print("Exception ====>>>>>>>> ", e)
            pass
            # return summary, unsupported_docs_

    return summary, unsupported_docs_

def list_all_files(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        # Modify 'dirs' in-place to exclude directories starting with a dot
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # Exclude files starting with a dot
            if not file.startswith('.'):
                if not file.endswith('.json') :
                    # Create the full file path and add it to the list
                    file_paths.append(os.path.join(root, file))
                
    return file_paths

# Apply the traceable decorator to track the function call in LangSmith
@traceable(run_type="llm",  name="TSD")
def tsd_main(tsd_repo_path, prompt_template):
    # Example template JSON
    template_json = {
        "database": {
            "tables": [
                {
                    "name": "",
                    "columns": [
                        {
                            "name": "",
                            "type": ""
                        }
                    ],
                    "relations": {}
                }
            ]
        },
        "backend": {
            "classes": [
                {
                    "name": "",
                    "description": "",
                    "type": "",
                    "inheritsFrom": "",
                    "methods": [
                        {
                        "name": "",
                        "description": ""
                    }
                    ],
                    "relations": {
                        "uses": [],
                        "connectsTo": []
                    }
                },
            ]
        },
        "frontend": {
            "components": [
                {
                    "name": "",
                    "type": "",
                    "parent": "",
                    "stateManagement": "",
                    "apiCalls": []
                }
            ]
        },
        "apiConnections": {
            "connections": [
                {
                    "frontendComponent": "",
                    "backendService": "",
                    "method": "",
                    "endpoint": "",
                    "requestData": {
                        "id": ""
                    },
                    "responseData": [
                        {
                            "hiringStatus": "",
                            "interviewDate": "",
                            "secondInterviewDate": "",
                            "doj": "",
                            "hiringComments": ""
                        }
                    ]
                }
            ]
        }
    }

    prompt_template = """
                You will be given content of file(s) from a repository and you have to perform following tasks.

                ### Task:
                1. **Generate a Detailed Expaination**:
                   - Integrate the current file(s) content into the Previous Explaination of the project, capturing all relevant changes, additions, or clarifications in the project structure.
                   - Ensure that the Details includes details about:
                     - The purpose and functionality of the current file(s) and previous details.
                     - Any relationships (e.g., dependencies, connections) between the current file(s) and other parts of the project (previous details).
                     - High-level design aspects such as the architecture, modules, services, and data flow.
                   - Provide an **overarching explanation** of the project's purpose, goals, and major components after processing this file(s) (as you will do this cumulatively across multiple files).

                2. **Update the JSON object**:
                   - Update the JSON object to reflect any new or updated information from the current file(s). It should also preserve previous details.
                   - Ensure that all relationships between backend, frontend, database, and API connections are updated.
                   - Maintain consistency in formatting and ensure the object adheres to the given template structure.

                3. **Generate a cumulative project explanation**:
                   - After processing all project files, generate a final **comprehensive project summary** that outlines:
                     - The entire architecture.
                     - Key functionalities of each component.
                     - Relationships between backend services, frontend components, databases, and APIs.
                     - How the components collaborate to achieve the overall project goals.
                   - Highlight key decisions or patterns used in the project (e.g., microservices, MVC, RESTful APIs, event-driven architecture).
                   - Include any insights regarding scalability, performance, or maintainability.

                
                You are given:
                1. **Current file(s) content**:
                   ```{current_file_content}```

                2. **Previous Explaination of the project and the JSON object**:
                   Previous Explaination:
                   ```{previous_summary}```

                3. **A JSON template** for representing the architecture, structure, and relationships of the project:
                   ```{json_template}```


                ### your are required to generate following Outputs:
                1. **Detailed Expaination of Project**:
                   - Ensure that the Details includes details about:
                     - The purpose and functionality of the components (e.g., dependencies, connections, database tables, classes).
                     - Any relationships (e.g., dependencies, connections, database tables, classes) between the components.
                     - High-level design aspects such as the architecture, modules, services, and data flow.
                   - Provide an **overarching explanation** of the project's purpose, goals, and major components after processing this file(s) (as you will do this cumulatively across multiple files).



                2. **Updated JSON object**:
                   - Present the updated JSON object based on the file(s) new content and any previous information.

                3. **Cumulative project summary**:
                   - Provide a comprehensive explanation that summarizes the entire project’s architecture, key components, and functionality.
                
                """



    # Initialize Langchain with Azure OpenAI
    llm = get_llm()
    files_to_process = list_all_files(tsd_repo_path)[:]

    # Process the files and update the JSON template iteratively
    final_summary,unsupported_docs = process_files(files_to_process, template_json, llm, prompt_template)

    return final_summary




if __name__ == "__main__":
    # tsd_repo_path = "./repos/Sphere/PTC/src/main/java/com/systemsltd/profiletracking/controller"
    # tsd_repo_path = "./repos/Sphere\PTC\bin\src\main\java\com\systemsltd\profiletracking\controller\JobOpeningsController.class"
    tsd_repo_path = "./repos/Sphere"

    # Define the dynamic prompt template (user-defined)
    prompt_template = """
                You will be given content of file(s) from a repository and you have to perform following tasks.

                ### Task:
                1. **Generate a Detailed Expaination**:
                   - Integrate the current file(s) content into the Previous Explaination of the project, capturing all relevant changes, additions, or clarifications in the project structure.
                   - Ensure that the Details includes details about:
                     - The purpose and functionality of the current file(s) and previous details.
                     - Any relationships (e.g., dependencies, connections) between the current file(s) and other parts of the project (previous details).
                     - High-level design aspects such as the architecture, modules, services, and data flow.
                   - Provide an **overarching explanation** of the project's purpose, goals, and major components after processing this file(s) (as you will do this cumulatively across multiple files).

                2. **Update the JSON object**:
                   - Update the JSON object to reflect any new or updated information from the current file(s). It should also preserve previous details.
                   - Ensure that all relationships between backend, frontend, database, and API connections are updated.
                   - Maintain consistency in formatting and ensure the object adheres to the given template structure.

                3. **Generate a cumulative project explanation**:
                   - After processing all project files, generate a final **comprehensive project summary** that outlines:
                     - The entire architecture.
                     - Key functionalities of each component.
                     - Relationships between backend services, frontend components, databases, and APIs.
                     - How the components collaborate to achieve the overall project goals.
                   - Highlight key decisions or patterns used in the project (e.g., microservices, MVC, RESTful APIs, event-driven architecture).
                   - Include any insights regarding scalability, performance, or maintainability.

                
                You are given:
                1. **Current file(s) content**:
                   ```{current_file_content}```

                2. **Previous Explaination of the project and the JSON object**:
                   Previous Explaination:
                   ```{previous_summary}```

                3. **A JSON template** for representing the architecture, structure, and relationships of the project:
                   ```{json_template}```


                ### your are required to generate following Outputs:
                1. **Detailed Expaination of Project**:
                   - Ensure that the Details includes details about:
                     - The purpose and functionality of the components (e.g., dependencies, connections, database tables, classes).
                     - Any relationships (e.g., dependencies, connections, database tables, classes) between the components.
                     - High-level design aspects such as the architecture, modules, services, and data flow.
                   - Provide an **overarching explanation** of the project's purpose, goals, and major components after processing this file(s) (as you will do this cumulatively across multiple files).



                2. **Updated JSON object**:
                   - Present the updated JSON object based on the file(s) new content and any previous information.

                3. **Cumulative project summary**:
                   - Provide a comprehensive explanation that summarizes the entire project’s architecture, key components, and functionality.
                
                """


    # Execute with dynamic prompt template
    response = tsd_main(tsd_repo_path, prompt_template)
    print(response)


