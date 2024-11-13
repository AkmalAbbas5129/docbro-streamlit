from langchain.document_loaders import TextLoader
import os
import json
from langsmith import traceable
from utils import get_llm


# Function to generate summary and update JSON with dynamic prompt template
def process_file(current_file_content, llm_model, prompt_template):
    # Format the dynamic prompt using the provided template
    prompt = prompt_template.format(
        current_file_content=current_file_content,
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
    for i, file_path in enumerate(files_batch):
        try:
            # Load the document using Langchain's TextLoader
            loader = TextLoader(file_path)
            documents = loader.load()

            # Assuming a single document is loaded
            document = documents[0]  # Extract the first (and likely only) document
            
            batch_document += "\n\n---------------------------------------------\n\n"+str(document)
        except:
            batch_document = ""

    return batch_document
        
# Main loop to iterate over files
def process_files(file_list, llm, prompt_template):
    
    batch_size = 4
    files_batches = make_batches(file_list, batch_size)
    
    summary = ""
    for i, files_batch in enumerate(files_batches):
        try:
            batch_document = load_documents_list(files_batch)
            if batch_document:
        #         print("batch_document:\n",batch_document)
                # print(f"\nProcessing batch {i + 1}/{len(files_batches)}: {files_batch}\n\n")

                # Update the JSON template and get a summary for each file
                summary = process_file(batch_document, llm, prompt_template)
            else:
                summary = "File type not supported"
        except Exception as e:
            # print("Exception ====>>>>>>>> ", e)
            return summary

    return summary



# Apply the traceable decorator to track the function call in LangSmith
@traceable(run_type="llm",  name="File Summary")
def summary_main(file_path):
    # Example template JSON
    prompt_template = """
                You are a highly skilled Senior Full Stack Developer with in-depth knowledge of software engineering, system architecture, and data structures. 
                Your role is to analyze files from a software project and progressively generate detailed explanations and structured data (JSON) that capture the key elements of the project.

                You are given:
                1. **Current file content**:
                   "{current_file_content}"

                "Using the provided file, thoroughly review the code to generate the following details: "
                "1. Dependencies - List down all the external libraries and internal dependencies used. "
                "2. Functions - Provide a list of all functions in the file, with a detailed explanation of each function's purpose and behavior. "
                "3. Classes - Provide a list of all classes in the file, with an explanation of their purpose, methods, and attributes. "
                "4. Code Structure - Explain the overall structure and flow of the code in the file, outlining how components interact. "
                "5. Summary - Create summary of the file. "
                """


    # Initialize Langchain with Azure OpenAI
    llm = get_llm()
    files_to_process = [file_path]

    # Process the files and update the JSON template iteratively
    final_summary = process_files(files_to_process, llm, prompt_template)

    return final_summary



if __name__ == "__main__":
    file_path = "./repos/Sphere/PTC/src/main/java/com/systemsltd/profiletracking/ProfileTrackingApplication.java"

    # Define the dynamic prompt template (user-defined)
    prompt_template = """
                You are a highly skilled Senior Full Stack Developer with in-depth knowledge of software engineering, system architecture, and data structures. 
                Your role is to analyze files from a software project and progressively generate detailed explanations and structured data (JSON) that capture the key elements of the project.

                You are given:
                1. **Current file content**:
                   "{current_file_content}"

                "Using the provided file, thoroughly review the code to generate the following details: "
                "1. Dependencies - List down all the external libraries and internal dependencies used. "
                "2. Functions - Provide a list of all functions in the file, with a detailed explanation of each function's purpose and behavior. "
                "3. Classes - Provide a list of all classes in the file, with an explanation of their purpose, methods, and attributes. "
                "4. Code Structure - Explain the overall structure and flow of the code in the file, outlining how components interact. "
                "5. Summary - Create summary of the file. "
                """

    # Execute with dynamic prompt template
    response = summary_main(file_path)
    print(response)


