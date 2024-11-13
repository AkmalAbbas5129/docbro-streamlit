from utils import load_template, get_llm, read_docx_as_markdown_from_dir
from crewai import Agent, Task, Crew, Process
from datetime import datetime
from langsmith import traceable
import PyPDF2





def call_brd_crew_kickoff(cleaned_transcript_content, template_content, rfp_content, relevant_docs, default_llm):

    if relevant_docs:
        is_data_missing = False
    else:
        is_data_missing = True

    key_points_extractor_agent = Agent(
        role="Key Points Extractor",
        goal="Efficiently extract and summarize all key points from the provided document, focusing on the most relevant and important information, "
             "and ensure clarity and accuracy in the extraction process.",
        allow_delegation=False,
        verbose=False,
        max_execution_time=None,
        llm=default_llm,
        backstory=(
            "You have a background in document analysis with strong skills in summarizing and distilling large amounts of information into "
            "concise, key points. You can quickly identify and prioritize the most important aspects of a document, ensuring that no critical "
            "details are overlooked. Your experience includes analyzing various types of documents, including RFPs, BRDs, and technical papers, "
            "and extracting the most relevant data points based on the context and the goal of the analysis."
        )
    )

    key_points_extractor_agent_task = Task(
        description="### Relevant Document containing some information ###\n"
                    + relevant_docs +
                    "\n\n From this Relevant Document extract all key points, summarizing the most important information "
                    "while ensuring accuracy and relevance. The key points should be clear and concise, covering all critical aspects of the document.",
        expected_output="Summary of the document, providing a clear and concise overview of the most important information.",
        condition=is_data_missing,
        agent=key_points_extractor_agent,
    )

    business_analyst = Agent(
        role="Business Analyst",
        goal="Effectively translate the meeting transcript, discussions and RFP document into a well-structured BRD using the provided template, "
             "ensuring it accurately captures project requirements and stakeholder needs as per the template attached.",
        allow_delegation=False,
        verbose=False,
        max_execution_time=None,
        llm=default_llm,
        backstory=(
            "You come from a background in business analysis, with experience in similar IT projects or a strong understanding "
            "of the organization's needs. Your skillset includes: You can effectively guide discussions and ensure everyone is "
            "on the same page, even in a technical environment. You possess the ability to translate complex information into "
            "clear and concise written documents. You can analyze information effectively, identify key requirements, and prioritize "
            "them based on importance. You possess a strong understanding of the provided BRD template and its purpose."
        )
    )

    subject_matter_expert = Agent(
        role="Subject Matter Expert",
        goal="Ensure the BRD accurately reflects the project's technical feasibility and translates technical discussions into "
             "actionable requirements for a successful IT project. Additionally, propose a clear and concise project name that "
             "captures the essence of the initiative.",
        allow_delegation=False,
        verbose=False,
        max_execution_time=None,
        backstory=(
            "You possess in-depth knowledge and experience specific to the project's domain (data analytics and integrations). While "
            "not directly involved in the initial meeting discussions, your expertise is crucial for refining the BRD's technical aspects "
            "and ensuring stakeholder needs are addressed."
        ),
        llm=default_llm
    )

    analyze_meeting_for_brd = Task(
        description=(
                "### Meeting Transcript ###\n"
                + cleaned_transcript_content +
                "\n### RFP Document ###\n"
                + rfp_content +
                "\nGiven above are the meeting transcript, RFP document and other relevant documents (From key_points_extractor_agent).\n"
                "1. Pay close attention to sections outlining functionalities, technical requirements, and references to specific technologies in both the "
                "transcript and the RFP.\n"
                "2. Analyze the technical aspects discussed in the transcript (e.g., data processing infrastructure updates, cloud migration) and assess "
                "their feasibility. Compare these with the requirements outlined in the RFP to ensure alignment. If needed, suggest alternative solutions "
                "or approaches to achieve the desired functionalities.\n"
                "3. Based on the transcript, the RFP, and your understanding of data analytics, translate the technical needs into clear and concise "
                "requirements within the BRD. This could include:\n"
                "   - Specific data points or sources needed for analysis.\n"
                "   - Functionality requirements for data ingestion, processing, and visualization.\n"
                "   - Integration requirements with existing systems.\n"
                "4. Review the stakeholder discussions in the transcript and the RFP (e.g., IT team's need for robust backend support, marketing team's "
                "need for advanced analytics features). Ensure the BRD reflects these needs by outlining functionalities that address them.\n"
                "5. Familiarize yourself with the BRD template's structure, sections, and required information for each section.\n"
                "6. Identify key points relevant to the BRD from both the transcript and the RFP, focusing on project background, goals, functionalities, "
                "success criteria, risks, and stakeholder needs as per template ###\n"
                + template_content +
                "\n###.\n"
                "7. Fill in the appropriate sections of the BRD template using the information extracted from both the transcript and the RFP.\n"
                "8. Ensure consistency and clarity throughout the document. Check for completeness and address any missing information. Consider using the "
                "transcript and the RFP to clarify details or resolve potential inconsistencies.\n"
        ),
        context=[key_points_extractor_agent_task],
        expected_output="A well-structured BRD, completed using the provided template, that accurately reflects the information captured in the "
                        "meeting transcript. This includes clearly defined requirements, identified stakeholder needs, success criteria, and a preliminary "
                        "understanding of project scope and risks.",
        agent=business_analyst,
    )

    sme_technical_review = Task(
        description=(
            "1. Pay close attention to sections outlining functionalities, technical requirements, and any references to specific technologies.\n"
            "2. Analyze whether the documented requirements align with technical constraints and capabilities. Identify any areas where the BRD "
            "might propose functionalities that are technically unrealistic or infeasible and add those in the BRD.\n"
            "3. If the BRD uses technical terms that might be unclear to non-technical stakeholders, propose alternative wording or explanations "
            "and update the BRD accordingly.\n"
            "4. Based on your expertise, anticipate and mention potential technical hurdles in the BRD that could arise during development based "
            "on the proposed requirements. Add mitigation strategies or alternative approaches in the BRD if necessary.\n"
            "5. Based on the project goals and functionalities discussed in the transcript, suggest a clear and concise name for the project. This "
            "name should accurately represent the initiative and be easily understood by all stakeholders."
        ),
        expected_output="A well-structured BRD, completed using the provided template, that accurately reflects the information captured in the "
                        "meeting transcript. This includes clearly defined requirements, identified stakeholder needs, success criteria, and a preliminary "
                        "understanding of project scope and risks.",
        agent=subject_matter_expert,
    )

    # Instantiate your crew
    brd_crew = Crew(
        agents=[key_points_extractor_agent, business_analyst, subject_matter_expert],
        tasks=[key_points_extractor_agent_task, analyze_meeting_for_brd, sme_technical_review],
        verbose=0,
        process=Process.sequential,  # Tasks will be executed one after the other
        planning=True,
        planning_llm=default_llm
    )

    # Begin the task execution
    result = brd_crew.kickoff()

    return result


@traceable(run_type="llm",  name="BRD")
def brd_main(brd_file_path, rfp_file_path, transcription_file_path, relevant_docs_path):
    if brd_file_path:
        if brd_file_path.endswith('.docx'):
            template_content = read_docx_as_markdown_from_dir(brd_file_path)
        else:
            template_content = load_template(brd_file_path)
    else:
        template_content = ""

    if transcription_file_path:
        if transcription_file_path.endswith('.docx'):
            cleaned_transcript_content = read_docx_as_markdown_from_dir(transcription_file_path)
        else:
            cleaned_transcript_content = load_template(transcription_file_path)
    else:
        cleaned_transcript_content = ""

    if relevant_docs_path:
        if relevant_docs_path.endswith('.docx'):
            relevant_docs = read_docx_as_markdown_from_dir(relevant_docs_path)
        else:
            relevant_docs = load_template(relevant_docs_path)
    else:
        relevant_docs = ""

    if rfp_file_path:
        # Open the PDF file
        with open(rfp_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Initialize an empty string to hold the text
            cleaned_rfp_content = ""

            # Iterate through the pages and extract text
            for page in range(len(reader.pages)):
                cleaned_rfp_content += reader.pages[page].extract_text()
    else:
        cleaned_rfp_content = ""

    default_llm = get_llm()
    result = call_brd_crew_kickoff(cleaned_transcript_content, template_content, cleaned_rfp_content, relevant_docs,
                                   default_llm)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # File name
    file_name = "./BRD-Docs/generated-brd/generated_brd_" + formatted_datetime + "_.md"

    # Save text to the markdown file
    with open(file_name, "w") as file:
        file.write(str(result))

    return str(result)

if __name__ == "__main__":

    brd_file_path = ""
    rfp_file_path = ""
    transcription_file_path = ""
    relevant_docs_path = ""


    response = brd_main(brd_file_path, rfp_file_path, transcription_file_path, relevant_docs_path)
    print(response)