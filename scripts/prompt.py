caption_wo_question = (
                    "As a senior editor, you have a task: Create a concise and comprehensive caption of the provided image, while adhering to these guidelines:\n"
                    "- Craft an caption that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness and as precise as possible.\n"
                    "- Given the title of this image as `{}`, your caption should be closely related to the title and the question.\n"
                    "- Incorporate main and essential information, eliminating extraneous language and focusing on critical aspects.\n"
                    "- Rely strictly on the provided image, the given title and the given question, without including external information.\n"
                    "- Format the caption in a single paragraph for easy reading and understanding.\n"
                    "- Conclude your caption with a single `*` as the indication of the end of the caption.\n"
                    )

caption_w_question = (
                    "You are an expert in information evaluation and critical thinking. Your task is to write a detailed caption for an image based on its title and a specific question, ensuring it provides enough context for someone to answer the question without seeing the image.\n"
                    "- Craft a highly descriptive caption directly related to the image, its title `{}`, and the given question `{}`.\n"
                    "- Ensure the caption highlights essential details, avoiding unnecessary information.\n"
                    "- Provide enough clarity so the question can be answered based on the caption alone.\n"
                    "- Do not introduce external information beyond what is in the image and its title.\n"
                    "- Structure the caption logically and step-by-step for easy understanding.\n"
                    "- End the caption with a single * to indicate completion."
                    )

text_isRel_instruction = '''
You are an expert in reading comprehension and logical reasoning. Your task is to give a clear, logical, and step-by-step explanation for the following conclusion about whether a given content and its title are related to a specific question. Please think carefully and provide a concise but logical explanation.

Objective: Determine whether a given content pair is related to a specific question.

You are provided with the following inputs:
1. Title: {The title to the text.}
2. Content: {A piece of text provided to you.}
3. Question: {A specific question that may or may not be related to the text.}

Based on this, provide a clear explanation with logical steps. Your response should include:
1. Reasoning: A step-by-step explanation of how you analyzed the text to determine if it is related to the question. It should end with '*' as a complete indication.
2. Response: A value (`True` or `False`) indicating whether the text is related to the question.

- **True**: The text is related and can help answer the question.
- **False**: The text is not related to the question.

Format your output as a JSON object:

-----
SCHEMA
-----
{
    "Reasoning": "Step-by-step reasoning explaining why the text is or isn't related to the question.",
    "Response": "True"/"False"
}

-----
EXAMPLE
-----
1. Title: Shigeru Miyamoto
2. Content: Shigeru Miyamoto (Japanese: 宮本 茂, Hepburn: Miyamoto Shigeru, born November 16, 1952) (pronounced [mʲijamoto ɕiŋeɾɯ̥; ɕiɡeɾɯ̥]) is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo. He is best known as the creator of some of the most critically acclaimed and best-selling video games and franchises of all time, such as Donkey Kong, Mario, The Legend of Zelda, Star Fox, F-Zero, and Pikmin.
3. Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?

Output:
{
    "Reasoning": "Step 1: The question asks for a Japanese video game designer and producer who is currently serving as the co-Representative Director of Nintendo and contributed to a game released in 1996 for the Nintendo 64. Step 2: The content introduces Shigeru Miyamoto, a Japanese video game designer and producer who holds the position of co-Representative Director at Nintendo, matching part of the question's criteria. Step 3: While the content does not directly mention Miyamoto's involvement in a specific game from 1996, his significant role in the creation of major games for Nintendo suggests relevance to the query. Step 4: The title confirms that the content is focused on Shigeru Miyamoto, further supporting the connection. Step 5: Despite the lack of a direct reference to the 1996 game, the question relates to the broader role of Miyamoto, and the content aligns with the information asked. Therefore, the content and title are sufficiently related to the question.*", 
    "Response": "True" 
}

-----

1. Title: Nintendo 64
2. Content: The provided image features the iconic logo of the Nintendo 64, a home video game console developed and marketed by Nintendo. The logo prominently displays the word ""NINTENDO"" in bold, blue capital letters, followed by the number ""64"" in red, signifying the console's 64-bit processor. Below the text, there is a three-dimensional, multicolored ""N"" composed of four interlocking shapes, each side colored differently in blue, green, red, and yellow. This design element not only emphasizes the brand but also symbolizes the innovative and playful nature of the console. The Nintendo 64, often abbreviated as N64, was known for its groundbreaking graphics and influential games, cementing its legacy in the gaming industry. The logo's vibrant colors and geometric design reflect the console's emphasis on advanced technology and entertainment.
3. Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?

Output:
{
    "Reasoning": "Step 1: The question asks for the name of a Japanese video game designer and producer who contributed to a Nintendo 64 game released in 1996 and currently serves as the co-Representative Director of Nintendo. Step 2: The content describes the Nintendo 64 logo and emphasizes the console's legacy but does not mention any individuals or specific contributors to the games. Step 3: While the content provides relevant information about the Nintendo 64 itself, it does not directly address the question about the producer. Step 4: The title 'Nintendo 64' is related to the console, but there is no reference to any game developer or producer in the content. Step 5: Since the required information about a specific individual is missing, the content is not related to the question.*", 
    "Response": "False"
}

-----

'''

image_isRel_instruction = """
You are an expert at problem solving, knowledge extraction, and reading comprehension. You excel at identifying requirements, breaking tasks down, and solving problems step-by-step.


Your objective is to determine whether the image content is directly related to answering the question. If the image and title are relevant, you should provide a thorough, step-by-step reasoning that clearly demonstrates the connection between the image content and the question. If the image is not relevant, explain why there is no connection.

Requirements:
- Craft a highly descriptive caption directly related to the image, its title, and the given question.
- Ensure the caption highlights essential details, avoiding unnecessary information.
- Provide enough clarity so the question can be answered based on the caption alone.
- Do not introduce external information beyond what is in the image and its title.
- Structure the caption logically and step-by-step for easy understanding.
- End the caption with a single * to indicate completion.

Given the following inputs:
1. Title: {Title of the image}
2. Question: {A given question}

Your output should adhere to the following JSON schema:

-----
SCHEMA
-----

{
    "Reasoning": "A detailed and logical step-by-step explanation of why the image content is or is not related to the question.",
    "Response": "True" / "False"
}

-----
EXAMPLES
-----

1. Title: 'The Cosby Show'
2. Question: 'What color is the inside of the text in The Cosby Show?'

Output:
{
  "Reasoning": "The image titled 'The Cosby Show' prominently displays the show's title. The inside of the text is white, standing out against a darker background. This contrast enhances visibility and aligns with the show's branding, making the title easily recognizable. The use of white inside the text reflects the cultural significance of the show's branding.*",
  "Response": "True"
}

-----

1. Title: 'Mercy (TV series)'
2. Question: 'Is the background to the Person of Interest (TV series) poster colored or colorless?'

Output:
{
  "Reasoning": "The image titled 'Mercy (TV series)' features a grayscale background, depicting a cityscape or a map-like layout. The only color in the image is a red triangular symbol, with the rest of the design focusing on muted tones. The colorless background reinforces the show's themes of surveillance and intrigue, creating a serious and dramatic tone. Therefore, the background is predominantly colorless. However, the question asking about the Person of Interest (TV series) poster, not about the Mercy (TV series), so the image does not seem to be related to the question.*",
  "Response": "False"
}

-----

"""

isSup_instruction = """
You are an expert in evaluating information and assessing the validity of responses. Your task is to determine whether a given answer is fully supported by the content and its title in relation to a specific question. The answer can be fully supported, partially supported, or not supported at all based on the provided content. Your evaluation must be logical, concise, and presented step-by-step, explaining how the content and its title relate to the question and answer. The explanation should end with '*' as a complete indication.

Objective: Assess whether the answer is fully supported by the content and its title for a given question. After evaluating, provide your judgment and an explanation for your choice.

Please evaluate the support level of the content for the answer according to the following levels:
1. True: The answer is fully supported by the content.
2. Partial: The answer is partially supported by the content; it may be incomplete or not entirely accurate but contains some correct elements.
3. False: The answer is not supported by the content or is contradicted by it.

Given the following inputs:
1. Context: {A context specific to the question, describing the content of the image or text.}
2. Question: {A specific question.}
3. Answer: {The proposed answer to the question based on the context.}

Output should be in the following JSON format:

-----
SCHEMA
-----

{
    "Reasoning": "Step-by-step reasoning explaining how the content and title support or fail to support the answer for the given question.",
    "Response": "True" / "Partial" / "False"
}
-----
EXAMPLE
-----

1. Context: "Pilotwings 64\nPilotwings 64 (Japanese: パイロットウイングス64, Hepburn: Pairottouingusu Rokujūyon) is a video game for the Nintendo 64, originally released in 1996 along with the debut of the console. The game was co-developed by Nintendo and the American visual technology group Paradigm Simulation. It was one of three launch titles for the Nintendo 64 in Japan as well as Europe and one of two launch titles in North America. Pilotwings 64 is a follow-up to Pilotwings for the Super Nintendo Entertainment System (SNES), which was a North American launch game for its respective console in 1991. Also like that game, Pilotwings 64 received production input from Nintendo producer Shigeru Miyamoto."
2. Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?
3. Answer: Shigeru Miyamoto


Output:
{
"Reasoning": "Step 1: The question asks for a Japanese video game designer and producer, currently the co-Representative Director of Nintendo, who contributed production input to a video game released for the Nintendo 64 in 1996. Step 2: The content mentions that 'Pilotwings 64,' a game released in 1996 for the Nintendo 64, received production input from Nintendo producer Shigeru Miyamoto. Step 3: Shigeru Miyamoto is also described as a Nintendo producer, which fits the role asked about in the question. Step 4: The title 'Pilotwings 64' relates directly to the content, which discusses the relevant video game mentioned in the question. Therefore, the content fully supports the answer provided.*",
"Response": "True"
}

-----

1. Context: "Shigeru Miyamoto\nShigeru Miyamoto (Japanese: 宮本 茂, Hepburn: Miyamoto Shigeru, born November 16, 1952) (pronounced [mʲijamoto ɕiŋeɾɯ̥; ɕiɡeɾɯ̥]) is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo. He is best known as the creator of some of the most critically acclaimed and best-selling video games and franchises of all time, such as Donkey Kong, Mario, The Legend of Zelda, Star Fox, F-Zero, and Pikmin."
2. Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?
3. Answer: Shigeru Miyamoto

Output:
{
"Reasoning": "Step 1: The question asks for a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who contributed to a video game for the Nintendo 64, originally released in 1996. Step 2: The content provides detailed information about Shigeru Miyamoto, confirming that he is a Japanese video game designer and producer, and currently holds the position of co-Representative Director of Nintendo. Step 3: However, the content does not mention any specific involvement of Miyamoto in a Nintendo 64 game released in 1996. Step 4: Since the content lacks a direct reference to the 1996 Nintendo 64 game mentioned in the question, it does not fully support the answer, even though Shigeru Miyamoto fits the role described. Therefore, the support is only partial.*",
"Response": "Partial"

-----

1. Content: "New York City Center\nThe image showcases the iconic New York City Center, a historic performing arts venue nestled among the towering skyscrapers of Manhattan. The building's distinctive architecture stands out with its blend of Art Deco and Neo-Moorish styles, featuring a light-colored stone facade with prominent arched entrances. The City Center's front is adorned with intricate details and a series of windows that hint at the grandeur within. The structure's unique roofline and decorative elements contrast sharply with the modern glass and steel high-rises surrounding it, creating a striking juxtaposition of old and new New York. The street scene captures the bustling urban environment, with yellow taxis and parked cars visible, as well as glimpses of greenery from nearby trees. The image effectively illustrates how the New York City Center has maintained its cultural significance and architectural integrity amidst the ever-evolving cityscape, serving as a beacon for the performing arts in the heart of one of the world's most dynamic metropolises."
2. Question: "What type of structure is shown in the bottom right corner of the New York City collage?"
3. Answer: "New York City Center"

Output:
{
    "Reasoning": "Step 1: The question asks about the structure shown in the bottom right corner of a New York City collage. Step 2: The content describes the New York City Center, detailing its architectural style, significance, and surroundings. Step 3: The answer provided is 'bridge,' which does not relate to the description of the New York City Center. Step 4: Since the content focuses solely on the New York City Center and does not mention any bridge, the answer is not supported at all by the content. Therefore, the support is false.*",
    "Response": "False"
}

-----

"""

isUse_instruction = """
You are an expert in analyzing information and assessing responses. Your task is to determine whether a given answer accurately addresses a question, based on the provided content. The content may or may not relate to the question, if the content is unrelated, the answer might be incorrect. Your goal is to logically and concisely evaluate the accuracy of the answer by comparing it with the content, following a clear, step-by-step approach. The explanation should end with '*' as a complete indication.

Objective: Determine whether a given answer accurately responds to a question, based on the provided content.

Given the following inputs:
1. Context: {The source material from which the answer is derived.}
2. Question: {A specific question that needs to be answered.}
3. Answer: {The provided answer in response to the question.}

Your goal is to determine whether the answer is appropriate by considering the following criteria:

1. **Format Accuracy**: The answer should be in the expected format. For example, if the question asks for a date, the answer should be presented in a date format.
2. **Logical Consistency**: The answer must be logically correct and align with the information provided in the content.

After your evaluation, provide a detailed explanation of your reasoning, breaking it down step by step, and offer a clear conclusion.

Your output should be in the following JSON format:
{
    "Reasoning": "A comprehensive explanation of whether the answer meets the expected format and logical criteria, supported by specific references to the content.",
    "Response": "True" / "False"
}

-----
Examples:
-----

1. Context: ```Pilotwings 64\nPilotwings 64 (Japanese: パイロットウイングス64, Hepburn: Pairottouingusu Rokujūyon) is a video game for the Nintendo 64, originally released in 1996 along with the debut of the console. The game was co-developed by Nintendo and the American visual technology group Paradigm Simulation. It was one of three launch titles for the Nintendo 64 in Japan as well as Europe and one of two launch titles in North America. Pilotwings 64 is a follow-up to Pilotwings for the Super Nintendo Entertainment System (SNES), which was a North American launch game for its respective console in 1991. Also like that game, Pilotwings 64 received production input from Nintendo producer Shigeru Miyamoto.```
2. Question: Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?
3. Answer: Shigeru Miyamoto

Output:
{
    "Reasoning": "Step 1: The question asks for a Japanese game designer, currently co-Representative Director of Nintendo, who contributed to a 1996 Nintendo 64 game. Step 2: The content states that 'Pilotwings 64,' released in 1996, received production input from Nintendo producer Shigeru Miyamoto. Step 3: The content links Shigeru Miyamoto directly to the production of 'Pilotwings 64,' aligning with the question's details. Step 4: While the content does not confirm Miyamoto's current role, it confirms his involvement in the game's production. Step 5: Given this connection, the answer 'Shigeru Miyamoto' is accurate.*",
    "Response": "True"
}

-----

1. Context: ```Nintendo 64\nThe logo prominently displays the word ""NINTENDO"" in bold, blue capital letters, followed by the number ""64"" in red, signifying the console's 64-bit processor. Below the text, there is a three-dimensional, multicolored ""N"" composed of four interlocking shapes, each side colored differently in blue, green, red, and yellow. This design element not only emphasizes the brand but also symbolizes the innovative and playful nature of the console. The Nintendo 64, often abbreviated as N64, was known for its groundbreaking graphics and influential games, cementing its legacy in the gaming industry. The logo's vibrant colors and geometric design reflect the console's emphasis on advanced technology and entertainment.```
3. Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?
4. Answer: Shigeru Miyamoto

Output:
{
    "Reasoning": "Step 1: The question seeks a Japanese game designer and producer who contributed to a Nintendo 64 game released in 1996. Step 2: The content focuses on the Nintendo 64 logo and design, with no mention of any individual involved in game development. Step 3: Since the content lacks information about Shigeru Miyamoto or any game production, the answer is unsupported. Step 4: Therefore, the answer 'Shigeru Miyamoto' is incorrect based on the content.*",
    "Response": "False"
}

------

"""

qa_instruction = '''
You are an expert in information evaluation and critical thinking. Your task is to find the answer to a given question from a passage of text. You must carefully read every word and think through each step without overlooking any details. Your output should contain two fields: `Reasoning` and `Response`. In `Reasoning`, document your logical thought process in a clear, concise manner. If you find the answer, write it in the `Response` field; if not, try your best to guess one. The `Reasoning` should end with '*' to indicate completion.

Objective: The task is to carefully analyze a passage of text to determine whether it contains the answer to a given question. The evaluation must be detailed, with clear reasoning, and identify the correct answer if present, or confirm its absence.

You are provided with the following inputs:

1. Context: {The text provided to you.}
2. Question: {The question that is being asked.}

Based on these inputs, provide a step-by-step explanation to identify the correct answer from the content. If you cannot find the answer in the passage, try to guess the answer. Your response should only contain the answer itself. Do not explain, provide notes, or include any additional text, punctuation, or preposition (e.g., 'on', 'at'), or articles (e.g., 'a', 'an', 'the') unless absolutely necessary.

Output format: 

-----
SCHEMA
-----

{
    "Reasoning": "Step-by-step reasoning explaining how the answer is inferenced to satisfy the question.",
    "Response": "The answer itself, as simple as possible."
}

-----

1. Context: ```Pilotwings 64\nPilotwings 64 (Japanese: パイロットウイングス64, Hepburn: Pairottouingusu Rokujūyon) is a video game for the Nintendo 64, originally released in 1996 along with the debut of the console. The game was co-developed by Nintendo and the American visual technology group Paradigm Simulation. It was one of three launch titles for the Nintendo 64 in Japan as well as Europe and one of two launch titles in North America. Pilotwings 64 is a follow-up to Pilotwings for the Super Nintendo Entertainment System (SNES), which was a North American launch game for its respective console in 1991. Also like that game, Pilotwings 64 received production input from Nintendo producer Shigeru Miyamoto.```
2. Question: Who is a Japanese video game designer and producer, currently serving as the co-Representative Director of Nintendo, who gave production input to a video game for the Nintendo 64, originally released in 1996 along with the debut of the console?

-----

output:

{
    "Reasoning": "The context mentions that 'Pilotwings 64' was a video game released in 1996 for the Nintendo 64. The game received production input from Nintendo producer Shigeru Miyamoto. This aligns with the question, which asks for a Japanese video game designer and producer who gave production input to a Nintendo 64 game released in 1996. Additionally, Shigeru Miyamoto is well known as a prominent figure at Nintendo and is currently serving as the co-Representative Director of the company. Therefore, the content fully supports that Shigeru Miyamoto is the correct answer to the question.*", 
    "Response": "Shigeru Miyamoto" 
}

-----

'''

