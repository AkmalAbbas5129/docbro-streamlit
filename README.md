# DocBro: Intelligent Documentation Assistant

## Description
DocBro is an intelligent documentation assistant designed to streamline the process of generating Business Requirement Documents (BRD),
Solution Design Documents (SDD), Test Cases, and Technical Summaries (TSD) from various input files. It leverages advanced AI capabilities to analyze documents,
extract key information, and produce structured outputs that meet project requirements.

## Installation
To set up the project, ensure you have Python 3.10 or higher installed. Then, clone the repository and install the required dependencies:

## Requirements

- Python 3.10+
- Azure OpenAI API Key
- Streamlit
- CrewAI
- LangChain
- LangSmith


```bash
git clone https://github.com/usman32466/DocBro.git
cd DocBro
pip install -r requirements.txt
```


### Dependencies
The project requires the following Python packages, which are listed in `requirements.txt`:

- `crewai`
- `crewai-tools`
- `langchain_community`
- `mammoth`
- `markdown`
- `python-dotenv`
- `streamlit`
- `PyPDF2`
- `python-docx`
- `markdownify`
- `streamlit-option-menu`
- `streamlit-markmap`
- `graphviz`
- `streamlit-react-flow`
- `streamlit-agraph`


### Folder Structure
Before running the application, create the following directories in your project root:

```
/BRD-Docs
    /brd-template
    /rfp-document
    /meeting-transcription
    /other
/SDD-Docs
    /sdd-template
    /sdd-meeting-transcription
    /other
/TestCase-Docs
    /generated_testcases
/repos
```

### Document Uploads
- **BRD-Docs**: Upload your BRD template, RFP documents, meeting transcriptions, and any other relevant documents in their respective folders.
- **SDD-Docs**: Upload your SDD template, generated BRD, meeting transcriptions, and any other relevant documents.
- **repos**: Upload your repositories (.zip files).
- **TestCase-Docs**: This folder will store generated test cases.

## Usage
To run the application, execute the following command in your terminal:

```bash
streamlit run app.py
```

Once the application is running, you can navigate through the different sections (BRD, SDD, TSD, Test Cases) using the sidebar menu. Each section provides options to upload documents and generate the respective outputs.

### Example Workflow
1. **Generate BRD**: Upload the BRD template and relevant documents, then click "Generate BRD" to create a structured BRD.
2. **Generate SDD**: Upload the SDD template and the generated BRD, then click "Generate SDD" to create a detailed SDD.
3. **Generate Test Cases**: Upload the generated BRD and SDD, then select the project repository to generate test cases.
4. **Generate TSD**: Upload the Project Repository, then click "Generate TSD" to create a detailed TSD.


## Project Structure
- **app.py**: The main application file that runs the Streamlit app and handles user interactions.
- **dockerfile**: Docker configuration for containerizing the application.
- **main_BRD.py**: Contains the logic for generating BRDs from uploaded documents.
- **main_SDD.py**: Contains the logic for generating SDDs based on BRDs and other inputs.
- **main_TSD.py**: Handles the generation of technical summaries (TSD) from project repositories.
- **main_testcase.py**: Manages the creation of test cases based on BRDs and SDDs.
- **main_Summary.py**: Provides functionality to summarize code files and generate structured outputs.
- **utils.py**: Contains utility functions for document processing and AI model integration.
- **requirements.txt**: Lists all the dependencies required for the project.


### Agents and Their Roles
- **Key Points Extractor**: Extracts and summarizes key points from documents.
- **Business Analyst**: Translates meeting transcripts and RFP documents into structured BRDs.
- **Solution Architect**: Converts BRDs into SDDs, ensuring technical feasibility.
- **Code Analyzer**: Analyzes code files to identify functions and classes, generating corresponding test cases.

## Code Explanation

### Main Components

- **Agent Definition**: Defines the roles and goals of the Business Analyst and SME agents.
- **Task Definition**: Specifies the tasks for each agent, including detailed instructions on how to process the meeting transcript and fill out the BRD template.
- **Crew Configuration**: Configures the agents and tasks within a hierarchical management process.
- **File Processing**: Handles the upload and conversion of meeting transcripts from `.docx` to markdown format.
- **Streamlit Interface**: Provides a user-friendly web interface for uploading files and displaying results.


## Configuration
The application does not require a separate configuration file. However, ensure that the necessary directories and document types are set up as described in the Installation section.

## Contributing
Contributions are welcome! If you would like to contribute to the project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.


