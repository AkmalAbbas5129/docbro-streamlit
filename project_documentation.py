from langchain.document_loaders import TextLoader
from langchain.schema import Document
import os
import json
from langchain_openai import AzureChatOpenAI, AzureOpenAI
from langsmith import traceable
from utils import get_llm, load_template


# # Function to generate summary and update JSON with dynamic prompt template
# def process_file(current_file_content, llm_model, prompt_template):
#     # Format the dynamic prompt using the provided template
#     prompt = prompt_template.format(
#         project_files=current_file_content
#     )
    

#     # Run the OpenAI model
#     response = llm_model(prompt)
    
#     # Extract the actual text from the response (AIMessage content)
#     response_content = response.content

#     return response_content

# def make_batches(file_list, batch_size):
#     """
#     Splits the list of file paths into batches of a specified size.

#     :param file_list: List of file paths.
#     :param batch_size: The number of files to include in each batch.
#     :return: A list of batches, where each batch is a list of file paths.
#     """
#     batches = [file_list[i:i + batch_size] for i in range(0, len(file_list), batch_size)]
#     return batches

# def load_documents_list(files_batch):
#     batch_document = ""
#     unsupported_docs = []
#     for i, file_path in enumerate(files_batch):
#         try:
#             # Load the document using Langchain's TextLoader
#             loader = TextLoader(file_path)
#             documents = loader.load()

#             # Assuming a single document is loaded
#             document = documents[0]  # Extract the first (and likely only) document
            
#             batch_document += "\n\n---------------------------------------------\n\n"+str(document)
#         except:
#             unsupported_docs.append(file_path)
        
#     return batch_document, unsupported_docs
        
# # Main loop to iterate over files
# def process_files(file_list, llm, prompt_template):
    
#     batch_size = 30
#     files_batches = make_batches(file_list, batch_size)
    
#     unsupported_docs_ = []
#     summary = ""
#     for i, files_batch in enumerate(files_batches):
#         try:
#             batch_document, unsupported_docs = load_documents_list(files_batch)
#             unsupported_docs_.extend(unsupported_docs)
#     #         print("batch_document:\n",batch_document)
#             # print(f"\nProcessing batch {i + 1}/{len(files_batches)}: {files_batch}\n\n")

#             # Update the JSON template and get a summary for each file
#             summary = process_file(batch_document, llm, prompt_template)
#         except Exception as e:
#             # print("Exception ====>>>>>>>> ", e)
#             pass
#             # return summary, unsupported_docs_

#     return summary, unsupported_docs_

# def list_all_files(directory):
#     file_paths = []
#     for root, dirs, files in os.walk(directory):
#         # Modify 'dirs' in-place to exclude directories starting with a dot
#         dirs[:] = [d for d in dirs if not d.startswith('.')]
        
#         for file in files:
#             # Exclude files starting with a dot
#             if not file.startswith('.'):
#                 if not file.endswith('.json') :
#                     # Create the full file path and add it to the list
#                     file_paths.append(os.path.join(root, file))
                
#     return file_paths

# def save_readme(content: str, filename: str = "README.md"):
#     """
#     Saves the given content to a README.md file.

#     Parameters:
#     - content (str): The text content for the README file.
#     - filename (str): The name of the file to save (default is 'README.md').

#     Returns:
#     - None
#     """
#     try:
#         with open(filename, "w") as file:
#             file.write(content)
#         print(f"{filename} saved successfully!")
#     except Exception as e:
#         print(f"An error occurred while saving {filename}: {e}")

# # Apply the traceable decorator to track the function call in LangSmith
# @traceable(run_type="llm",  name="TSD")
# def tsd_main(tsd_repo_path):

#     prompt_template = """
#                 Context: You are an expert in creating clear and informative README files for software projects. 
#                 This project contains several files with various functions. Your task is to create a README.md file that provides 
#                 an overview of the project, its purpose, setup instructions, usage guidelines, and any other relevant information. 
#                 Make it accessible and easy to understand for users who might want to contribute or utilize the project.

#                 Files Content: {project_files}

#                 Instructions:
#                 1. Start with a clear **Project Title** and **Description** section that explains the main purpose and functionality of the project.
#                 2. Add an **Installation** section explaining any dependencies from `requirements.txt` and setup steps.
#                     - Also add which folders should be created before and what kind of documnets it should have or should be uploaded to these folders.
#                 3. Include a **Usage** section with examples or basic instructions on how to use the project.
#                 4. Describe each file and module in a **File Structure** or **Project Structure** section, summarizing the purpose of each and explaining how they relate to each other. For example what agents are being used and how the are working.
#                 5. Add a **Configuration** section to explain any configurable parameters in `config.yaml`.
#                 6. Provide a **Contributing** section with guidelines for contributing to the project, if applicable.
#                 7. Include a **License** section with a note about the project license if needed.

#                 Format your response in Markdown.

#                 """



#     # Initialize Langchain with Azure OpenAI
#     llm = get_llm()
#     # tsd_repo_path = "./repos/Sphere/PTC/src/main/java/com/systemsltd/profiletracking"
#     files_to_process = list_all_files(tsd_repo_path)[:]

#     # Process the files and update the JSON template iteratively
#     final_summary,unsupported_docs = process_files(files_to_process, llm, prompt_template)
#     save_readme(final_summary, "README.md")

#     return final_summary
#     # return "hehehhehe"




# if __name__ == "__main__":
#     tsd_repo_path = "./DocBro"

#     # Execute with dynamic prompt template
#     response = tsd_main(tsd_repo_path)
#     print(response)


if __name__ == "__main__":
    tsd_repo_path = "./BRD-Docs/brd-template/brd-template.md"

    # Execute with dynamic prompt template
    response = load_template(tsd_repo_path)
    print(response)


