from crewai import Agent, Task, Crew, Process
import PyPDF2
from datetime import datetime
from utils import load_template, get_llm, read_docx_as_markdown_from_dir
from langsmith import traceable


def call_crew_kickoff(cleaned_transcript_content, template_content, rfp_content, cleaned_brd_content, relevant_docs,
                      default_llm):
    #####-------------------Agents ------------------------------>>>>>>>>>>>>>>>>

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

    rfp_summarizer = Agent(
        role="RFP Summarizer",
        goal="Summarize the key points of the RFP document, focusing on the project objectives, scope, technical requirements,"
             " and vendor qualifications. Ensure that the summary is clear, concise, and captures the essence of the RFP.",
        allow_delegation=False,
        verbose=False,
        backstory=(
            "You possess a strong understanding of project management and procurement processes. Your expertise allows you to distill complex RFP "
            "documents into summaries that highlight critical information for stakeholders to make informed decisions."
        ),
        llm=default_llm
    )

    solution_architect = Agent(
        role="Solution Architect",
        goal="Effectively translate the BRD, along with key insights from meeting discussions and the RFP summary, "
             "into a well-structured Solution Design Document (SDD) using the provided template."
             "Ensure the SDD accurately captures the technical solution, architecture, and implementation details, "
             "aligning with the project requirements and stakeholder needs as outlined in the BRD.",
        allow_delegation=False,
        verbose=False,
        llm=default_llm,
        backstory=(
            "You come from a background in solution architecture, with experience in similar IT projects and a strong understanding"
            "of the organization's technical needs. Your skillset includes: effectively guiding discussions and ensuring alignment"
            "among stakeholders, even in complex technical environments. You have the ability to translate intricate technical concepts"
            "into clear and actionable design documents. You excel at analyzing technical information, identifying key architectural requirements,"
            "and prioritizing them based on system impact and project goals."
            "You possess a deep understanding of the provided SDD templates and their purposes."
        )
    )

    subject_matter_expert = Agent(
        role="Subject Matter Expert",
        goal="Ensure the SDD accurately reflects the project's technical feasibility and translates technical discussions into "
             "actionable requirements for a successful IT project.",
        allow_delegation=False,
        verbose=False,
        llm=default_llm,
        backstory=(
            "You possess in-depth knowledge and experience specific to the project's domain ( Project Solutioning ). While "
            "not directly involved in the initial meeting discussions, your expertise is crucial for refining the SDD's technical aspects "
            "and ensuring stakeholder needs are addressed."
        )
    )

    #####-------------------Tasks ------------------------------>>>>>>>>>>>>>>>>

    summarize_rfp_task = Task(
        description=(
                "### RFP Document ###\n"
                + rfp_content +
                "\nGiven above is the RFP document.\n"
                "1. Carefully review the RFP document and identify the key sections, including project objectives, scope of work, technical requirements, "
                "vendor qualifications, and submission guidelines.\n"
                "2. Summarize each section, focusing on the most critical information that will help stakeholders understand the project's goals and "
                "requirements.\n"
                "3. Ensure that the summary is concise, clear, and captures the essence of the RFP, making it easier for decision-makers to evaluate the "
                "proposal.\n"
                "4. Highlight any unique or critical requirements that may affect the project’s execution or vendor selection.\n"
                "5. Provide a final summary that offers a high-level overview of the entire RFP document."
        ),
        expected_output=(
            "A well-structured summary of the RFP document, including concise descriptions of the project objectives, scope, technical requirements, "
            "vendor qualifications, and any critical requirements. The summary should be clear and actionable, providing stakeholders with a quick "
            "understanding of the RFP's key points."
        ),
        agent=rfp_summarizer,
    )

    analyze_brd_for_sdd = Task(
        description=(
                "### Meeting Transcript ###\n"
                + cleaned_transcript_content +
                "\nGiven above are the meeting transcript.\n"
                "###" + cleaned_brd_content + "###\n"
                                              "Given above is the BRD, meeting transcript and other relevant documents (From key_points_extractor_agent)\n"
                                              "1. Pay close attention to sections outlining functionalities, technical requirements, system architecture, and references to specific technologies.\n"
                                              "2. Analyze the technical aspects discussed in the transcript and assess their feasibility."
                                              "If needed, suggest alternative solutions or approaches to achieve the desired system architecture and functionalities.\n"
                                              "3. Based on the transcript, BRD, RFP summary and your understanding of solution architecture, translate the technical needs into clear and concise requirements within the SDD. This could include:\n"
                                              "- Specific technical components or systems required for implementation."
                                              "- Architectural requirements for data ingestion, processing, and storage."
                                              "- Integration points with existing systems and technologies."
                                              "- System scalability, security, and performance considerations.\n"
                                              "4. Review the stakeholder discussions in the transcript. Ensure the SDD reflects these needs by outlining the technical solutions and architecture that address them.\n"
                                              "5. Familiarize yourself with the template's structure, sections, and required information for each section.\n"
                                              "6. Identify key points relevant to the SDD, focusing on system architecture, design components, integration points,"
                                              "technical risks, and implementation details as per template ###\n" + template_content + "\n###.\n"
                                                                                                                                       "7. Fill in the appropriate sections of the SDD template using the information extracted from the transcript.\n"
                                                                                                                                       "8. Ensure consistency and clarity throughout the document. Check for completeness and address any missing information."

        ),
        context=[key_points_extractor_agent_task, summarize_rfp_task],
        expected_output="A well-structured SDD, completed using the provided template, should accurately reflect the technical information captured in the BRD."
                        "This includes clearly defined system architecture, detailed technical requirements, identified stakeholder needs, success criteria,"
                        "and a comprehensive understanding of project scope, risks, and potential solutions.",
        agent=solution_architect,
    )

    sme_technical_review = Task(
        description=(
            "1. Pay close attention to sections outlining functionalities, technical requirements, system architecture, and any references to specific technologies.\n"
            "2. Analyze whether the documented architecture and technical requirements align with the system's constraints and capabilities. Identify any areas where"
            "the SDD might propose solutions that are technically unrealistic or infeasible and address those within the SDD."
            "3. If the SDD uses technical terms that might be unclear to non-technical stakeholders, propose alternative wording"
            "or explanations and update the SDD accordingly.\n"
            "4. Based on your expertise, anticipate and document potential technical hurdles in the SDD that could arise during development"
            "based on the proposed architecture and requirements. Add mitigation strategies or alternative approaches in the SDD if necessary."
            "5. Based on the project goals, architecture, and functionalities discussed in the transcript."
        ),
        expected_output=(
            "Comprehensive and refined SDD document,completed using the provided template, should accurately reflect the technical information captured in the BRD."
            "This includes clearly defined system architecture, detailed technical requirements, identified stakeholder needs, success criteria,"
            "and a comprehensive understanding of project scope, risks, and potential solutions."),
        agent=subject_matter_expert,
    )

    # Instantiate your crew
    brd_crew = Crew(
        agents=[key_points_extractor_agent, rfp_summarizer, solution_architect, subject_matter_expert],
        tasks=[key_points_extractor_agent_task, summarize_rfp_task, analyze_brd_for_sdd, sme_technical_review],
        verbose=0,
        # manager_llm=default_llm,
        # process=Process.hierarchical,
        process=Process.sequential,  # Tasks will be executed one after the other
        planning=True,
        planning_llm=default_llm
    )

    # Begin the task execution
    result = brd_crew.kickoff()

    return result


@traceable(run_type="llm",  name="SDD")
def sdd_main(sdd_template_file_path, generated_brd_file_path, rfp_file_path, transcription_file_path,
             relevant_docs_path):

    if sdd_template_file_path:
        if sdd_template_file_path.endswith('.docx'):
            template_content = read_docx_as_markdown_from_dir(sdd_template_file_path)
        else:
            template_content = load_template(sdd_template_file_path)
    else:
        template_content = ""

    if transcription_file_path:
        if transcription_file_path.endswith('.docx'):
            transcript_content = read_docx_as_markdown_from_dir(transcription_file_path)
        else:
            transcript_content = load_template(transcription_file_path)
    else:
        transcript_content = ""

    if generated_brd_file_path:
        if generated_brd_file_path.endswith('.docx'):
            brd_content = read_docx_as_markdown_from_dir(generated_brd_file_path)
        else:
            brd_content = load_template(generated_brd_file_path)
    else:
        brd_content = ""

    if relevant_docs_path:
        if relevant_docs_path.endswith('.docx'):
            relevant_docs = read_docx_as_markdown_from_dir(relevant_docs_path)
        else:
            relevant_docs = load_template(relevant_docs_path)
    else:
        relevant_docs = ""

    # read RFP document (pdf)
    with open(rfp_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Initialize an empty string to hold the text
        rfp_content = ""

        # Iterate through the pages and extract text
        for page in range(len(reader.pages)):
            rfp_content += reader.pages[page].extract_text()

    default_llm = get_llm()

    # start Crew to generate SDD
    result = call_crew_kickoff(transcript_content, template_content, rfp_content, brd_content, relevant_docs,
                               default_llm)

    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # File name
    file_name = "./SDD-Docs/generated-sdd/generated_sdd_" + formatted_datetime + "_.md"

    # Save text to the markdown file
    with open(file_name, "w") as file:
        file.write(str(result))

    return str(result)
