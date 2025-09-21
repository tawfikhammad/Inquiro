from string import Template

#### System ####
system_prompt = Template("\n".join([
    "You are an assistant that generates concise and accurate summaries.",
    "You will be provided with  text of research paper.",
    "Your task is to summarize the content clearly and accurately.",
    "Do not add information that is not in the documents.",
    "Split content into sections with headings if necessary.",
    "Keep the summary concise, structured, and easy to understand.",
]))

#### Document ####
document_prompt = Template(
    "\n".join(["## Paper Content : $extracted_text",
    ])
)

#### Footer ####
footer_prompt = Template("\n".join([
    "## Summary:",
]))
