# Deepgrade-AI-Grading-System
An automated grading system tool that mitigates individual LLMs drawbacks with AI agent architecture and systems solutions

## Architecture Diagram

```mermaid
flowchart LR
    A[In] -->B[LLM Call 1]
    B[LLM Call 1] -->|Output 1|C[Gate]
    C[Gate] -->|Pass| D[LLM Call 2]
    C[Gate] -->|Fail| B[LLM Call 1]
    D[LLM Call 2] -->|Pass| E[LLM Call 3]
```

## Consistency Rule Engine Architecture

```mermaid
flowchart LR
    A["Flowchart Image Input"] --> B["Extraction Model<br/>(llama3.2-vision)"]
    B --> C["Extract Raw JSON"]
    C --> D["Normalize JSON Structure"]
    D --> E["LLM Node Classification<br/>(granite3.2-vision)"]
    E --> F["Update JSON with Classified Types"]
    F --> G["Graph-Based Logic Evaluation"]
    G --> H["Run Logic Tests:<br/>• Start/End Check<br/>• Decision Condition<br/>• Connectivity<br/>• Sequence Order<br/>• Decision Outcomes<br/>• Self-Loops<br/>• Text Presence"]
    H --> I["Aggregate & Normalize Scores"]
    I --> J["Output Final Score, Details & Updated JSON"]
```
### We use a logic gateway based verificaition of the output before moving along the prompt chaining approach.

## Multi LLM Orchestration Tool Architecture Diagram
```mermaid
flowchart LR
    A[Input] -->B[Prompt Classification]
    
    subgraph Sematic Classifer
    B[Prompt Classification:
    Summerization
    Logic Verification
    Information Extration
    Reasoning
    Localization Recognition] -->|Prompt type|C[Input + Meta data]
    end
    C[Input + Meta data] -->D[Orchestration tool]
    A[Input] -->|Prompt|C[Input + Meta data]
    D[Orchestration tool] -->|Pass| E[Benchmarking tool]
    E[Benchmarking tool] -->|Returns Evaluations| D[Orchestration tool]
    D[Orchestration tool] -->|Output| F[LLM Call 1]
    D[Orchestration tool] -->|Output| G[LLM Call 2]
    D[Orchestration tool] -->|Output| H[...]
    F --> J[Synthesizer]
    G --> J[Synthesizer]
    H --> J
    J --> K[Output]
```

## Roadmap
Here's a glimpse of what's on the horizon:
| Feature                                   | Status          |
|-------------------------------------------|-----------------|
| **Website design**       | ✅ Completed    |
| **Setup README.MD**           | ✅ Completed    |
| **LLMs Research**           | ✅ Completed    |
| **Backend Integration**              |  📝 Planned   |
| **Logic Gateway code - Graph Analysis**              |  🔄 In Progress  |
| **FlowCE Evaluation Code (Benchmarking mechanism)**              |  📝 Planned   |
| **Orchestration tool**              |  📝 Planned   |

Status:
✅ Completed
📝 Planned
🔄 In Progress

# Design notes - UI/UX (Faizal)
![image](https://github.com/user-attachments/assets/b02ddeeb-422b-4482-ad1c-99f3ea11a947)
![image](https://github.com/user-attachments/assets/58cd8ff4-c391-4442-9474-4c7d78ce9b85)

# Developer notes - LLMs Research (Keertish)

## Setup of ollama and test case
Setup local multi model solution to test quality and responses of model. Downloaded the ![image](https://github.com/user-attachments/assets/228ff3c6-f958-4160-91dd-9758c811bd69) llama model with 7b. Now, selecting a image to test out the model. The image is taken from a bigger dataset that primary tested on reasoning of LLM model. This is the repo [FlowCV] (https://github.com/360AILAB-NLP/FlowCE). We took one image which is ![flowchart_test](https://github.com/user-attachments/assets/3387fa4c-da76-4f37-ac2b-7e357ceacc13)

## Tested out on llama
Here's the test response from llama and my comments. 
![image](https://github.com/user-attachments/assets/03231278-7c68-4494-8859-be44b57b32ae)


Hence, we have confirmed that the multi model LLMs on it's own isn't configured for verification and logical validation. Hence, the next step of action is to use the model for it's purpose here being to extract information from the image.

![image](https://github.com/user-attachments/assets/e59e7468-3564-4881-ae3b-a1f543eba9a7)

We observe extensive datalose and organization error. Eg. Point 3 is a hallucination. The question branches into only 2 options yet it states that it branches into 3. While the the question itself merges multiple boxes. Extensive summerization and jumping logics leading to higher data loss before moving onto the next stage. Please refer the initial image to notice the failings of the current state of LLMs. ![image](https://github.com/user-attachments/assets/4aa530f9-9e50-4163-93c9-86e9054c2bd7)


## Tested out on Gemini 2.0 Flash
We now test out the same sample data on a Gemini 2.0 Flash Powered LLM to see it's response.

![Screenshot 2025-02-15 190543](https://github.com/user-attachments/assets/8e10b9c1-4b53-4bbb-8a32-205e599a4967)

As, mentioned the response created a unending cycle within the data extracted. It does improve upon the overall structure but doesn't notice the logical fallacy of an unending loop/cycle. Again as an in depth explaination. ![image](https://github.com/user-attachments/assets/ccabc271-ce5d-4b5d-8a2b-9a179ea7dd68)

When "Is the fault rectified?" responses no, it's supposed to go onto the next conditional block being "Does the system receive many TC BPDUs?" but instead it goes back to the "Analyze packet characteristics and filter out attack packets" which in turn creates the loop. We can also attribute that the sample image itself has faults but the general consensus is the flowcharts are stated this way. We could use this as a data point to fine to models to not the irregularity which taking the image as an input. But, the alternative arguement could be that with a better logic based validation or verfication mechanism we could have avoided this mistake.

## Tested out on ChatGPT o3-mini-high
Next, we try out the sample image in a ChatGPT o3-mini-high ![image](https://github.com/user-attachments/assets/26b3aac8-310d-4c4e-9157-a5008a7922ca) The data extraction phase does solve the error noticed in Gemini 2.0 Flash model. The model does a great data extraction phase. It passes my human validation of all conditional points and flow. It also gives a great response on the verification and validation front. ![image](https://github.com/user-attachments/assets/cacaad8b-acbd-41c5-bfe3-447873c1ade5)

## Tested out on llama3.2-vision 11b model
![image](https://github.com/user-attachments/assets/97b54322-66e3-4d96-8f84-aa8373e3cb50)

The extraction worked well and held onto the reasoning aspect as well. We can proceed with chain of thought reasoning from this output. We can also validate the input + image prompt on the llama3.2vision 11b model as well. Then compare the improvements in a multi llm orchestration scenario.

## Developer Notes - Frontend (Esha)
Version 1:
![image](https://github.com/user-attachments/assets/34813e0c-13e8-4a11-b3d7-565e911e10ab)

Version 2:
![image](https://github.com/user-attachments/assets/e7163923-a172-48de-8643-3f331b59651f)



