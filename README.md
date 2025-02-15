# Deepgrade-AI-Grading-System
An automated grading system tool that mitigates individual LLMs drawbacks with AI agent architecture and systems solutions

# Developer notes (Keertish)
Setup local multi model solution to test quality and responses of model. Downloaded the ![image](https://github.com/user-attachments/assets/228ff3c6-f958-4160-91dd-9758c811bd69) llama model with 7b. Now, selecting a image to test out the model. The image is taken from a bigger dataset that primary tested on reasoning of LLM model. This is the repo [FlowCV] (https://github.com/360AILAB-NLP/FlowCE). We took one image which is ![flowchart_test](https://github.com/user-attachments/assets/3387fa4c-da76-4f37-ac2b-7e357ceacc13)

Here's the test response from llama and my comments. 
![image](https://github.com/user-attachments/assets/5afb79ad-f06d-4c47-a139-350f2dfb7374)

Hence, we have confirmed that the multi model LLMs on it's own isn't configured for verification and logical validation. Hence, the next step of action is to use the model for it's purpose here being to extract information from the image.

![image](https://github.com/user-attachments/assets/e59e7468-3564-4881-ae3b-a1f543eba9a7)

We observe extensive datalose and organization error. Eg. Point 3 is a hallucination. The question branches into only 2 options yet it states that it branches into 3. While the the question itself merges multiple boxes. Extensive summerization and jumping logics leading to higher data loss before moving onto the next stage. Please refer the initial image to notice the failings of the current state of LLMs. ![image](https://github.com/user-attachments/assets/4aa530f9-9e50-4163-93c9-86e9054c2bd7)

We now test out the same sample data on a Gemini 2.0 Flash Powered LLM to see it's response.

![Screenshot 2025-02-15 190543](https://github.com/user-attachments/assets/8e10b9c1-4b53-4bbb-8a32-205e599a4967)

As, mentioned the response created a unending cycle within the data extracted. It does improve upon the overall structure but doesn't notice the logical fallacy of an unending loop/cycle. Again as an in depth explaination. ![image](https://github.com/user-attachments/assets/ccabc271-ce5d-4b5d-8a2b-9a179ea7dd68)

When "Is the fault rectified?" responses no, it's supposed to go onto the next conditional block being "Does the system receive many TC BPDUs?" but instead it goes back to the "Analyze packet characteristics and filter out attack packets" which in turn creates the loop. We can also attribute that the sample image itself has faults but the general consensus is the flowcharts are stated this way. We could use this as a data point to fine to models to not the irregularity which taking the image as an input. But, the alternative arguement could be that with a better logic based validation or verfication mechanism we could have avoided this mistake.

Next, we try out the sample image in a ChatGPT o3-mini-high ![image](https://github.com/user-attachments/assets/26b3aac8-310d-4c4e-9157-a5008a7922ca). The data extraction phase does solve the error noticed in Gemini 2.0 Flash model. The model does a great data extraction phase. It passes the my human validation of all conditional points and flow. It also gives a great response on the verification and validation front. ![image](https://github.com/user-attachments/assets/cacaad8b-acbd-41c5-bfe3-447873c1ade5)




