# DocInsight: Intelligent Document Analysis and Q&A System

## 📖 Project Overview
This project, **DocInsight**, is designed to enable **semantic search across multiple PDF documents**, followed by **LLM-powered summarization and answer generation**. It leverages vector similarity to identify semantically relevant text chunks and constructs logical, concise responses using a large language model.

## 🎯 Project Objectives
- Enable users to quickly find relevant information through **semantic search**.
- Provide **LLM-powered summarization** of retrieved documents for coherent and logical answers.
- Develop a **browser-accessible web interface**.
- Utilize **Docker for containerized deployment** to ensure easy setup and execution.

## ✨ Key Features
- **Semantic Search**: Retrieves the most relevant chunks from uploaded PDFs using embedding-based similarity.
- **LLM Integration**: Summarizes and constructs coherent answers based on the selected chunks.
- **Multi-file Support**: Capable of handling multiple PDF files uploaded via browser interface.
- **Browser-based Interface**: Built for accessibility and convenience directly from the web.
- **Semantic Query Classification**: Classifies incoming queries as `summary`, `comparison`, or `normal`.
- **Original Context Preview**: Returns original document chunks along with generated summaries and comparisons for traceability.
- **File Selection for Targeted QA**: Allows users to manually select which uploaded PDF files to include in a query.
- **Smarter Context Selection**: Enhanced chunking logic including paragraph-based, deduplication, diversity filtering, Head-Tail inclusion, document-type detection, and section-aware chunking.
- **Re-ranking**: Implemented re-ranking of chunks retrieved by FAISS using cosine similarity for improved accuracy.

## 🛠️ Tech Stack
- **Programming Language**: Python
- **Containerization**: Docker & Docker Compose
- **PDF Processing**: `PyMuPDF` / `pdfplumber`
- **Embeddings & Semantic Search**: `SentenceTransformers`, `FAISS`
- **LLM Inference**: OpenAI API / Local models (optional)
- **Backend API**: FastAPI
- **Frontend UI**: Streamlit

## 🚀 Development & Execution
### 1. Clone the Repository
```bash
git clone https://github.com/coisu/docInsight.git
cd docInsight
```

### 2. Run the Docker Containers
> The `.env` file is encrypted using GDG, and you'll need the decryption password to load environment variables.
> You would need your own OPENAI_API_KEY setting.

```bash
make build
make run
```

### 3. Access the Web Interface
- Streamlit UI (User Interface): `http://localhost:8501`
- FastAPI Swagger UI (API Documentation): `http://localhost:8000/docs`

## 🔬 Latest Test Results & Analysis (Reflecting 02/06/2025 Updates)

This section includes results from tests conducted after implementing semantic query classification, improved chunking logic, and re-ranking.

**Test Target Files (General Sources):**
* `RoBERTa.pdf` (Presumed: "RoBERTa: A Robustly Optimized BERT Pretraining Approach" by Liu et al. - *Source: Google Scholar / arXiv*)
* `language_understanding_paper.pdf` (Presumed: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding" by Devlin et al. - *Source: Google Scholar / arXiv*)
* `1810.04805v2.pdf` (BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding - *Source: Google Scholar / arXiv*)
* `main.pdf` ("Sentiment Analysis using Bidirectional LSTM Network" - *Source: Google Scholar / ScienceDirect*)
* `d572e43d0c120d59e81c228f2a17b3b05006.pdf` ("Text based Sentiment Analysis using LSTM" - *Source: Google Scholar / IJERT*)
* `Analyzing the Performance of Sentiment Analysis using BERT, DistilBERT, and RoBERTa.pdf` - *Source: Google Scholar / IEEE Xplore*
* `W19-6120.pdf` ("Aspect-Based Sentiment Analysis Using BERT" - *Source: Google Scholar / ACL Anthology*)
* `19967-pdf.pdf` ("Beauty and the Beast" by Anonymous - *Source: Project Gutenberg*)
* `2505.22680v1.pdf` ("Exploring Holography in Neuro-Vascular Dynamics" - *Source: arXiv*)

### Multi-document Based Test (User Provided Screenshots Summary)

#### Question 1: Multi-document Summary
> Query: "Help me understand the general direction of these documents."
> *This query was intentionally designed to avoid direct keywords like “summarize” to test whether the classification via semantic embeddings works as expected.*

* **System Result Analysis:**
    * Query Type Classification: Correctly identified as `summary`. This demonstrates the semantic classifier is working as intended.
    * Answer Content: Provided summaries for each uploaded document and included toggleable views to inspect the original document chunks used to generate the summaries. Screenshots (`multiple_sum_1`, `multiple_sum_2`, `multiple_sum_3`) show that per-document summaries were well-generated.
    * Accuracy: High. The system accurately grasped the query's intent and successfully performed the requested multi-document summarization. The source traceability feature also appears to be functioning well.

#### Question 2: Multi-document Differentiation
> Query: "What are the key takeaways that distinguish each paper?"
> *Although the query does not include direct comparison keywords like “compare” or “difference”, it was accurately classified as a `comparison` thanks to the semantic understanding logic.*

* **System Result Analysis:**
    * Query Type Classification: Correctly identified as `comparison`.
    * Answer Content: The system returned a structured, multi-part answer including: an overall topic summary, per-document summaries, key differences, commonalities, and insights/implications. Toggleable views for original source chunks were also provided. Screenshots (`multiple_diff_ans1`, `multiple_diff_ans2`) show these structured answers were well-generated.
    * Accuracy: High. The system accurately understood the intent of the indirect comparison query and provided a detailed, structured comparative analysis.

#### Section-Based Chunking and Re-ranking Improvement Test Results

**Test Case 1:**
> Query: "What are the key differences in the training objectives between BERT and RoBERTa?"

* **Analysis of "Before" Answer (RAG System):** Stated that the document does not provide explicit information on RoBERTa's training objectives.
* **Analysis of "After" Answer (RAG System):** Accurately explained specific differences, such as RoBERTa's data processing, optimization techniques, removal of the NSP objective, use of dynamic masking patterns, longer sequences, and larger batch sizes.
* **Review:**
    * Accuracy (After Improvement): High. The improved chunking and re-ranking logic allowed more accurate and detailed information to be found and provided to the LLM, significantly enhancing the answer quality.

**Test Case 2:**
> Query: "Compare the experimental results of BERT and RoBERTa on GLUE and SQuAD benchmarks."

* **Analysis of "Before" Answer (RAG System):** Stated that specific experimental result comparison was not possible, offering only some qualitative remarks.
* **Analysis of "After" Answer (RAG System):** Correctly noted the absence of explicit numerical comparison in the document, but still provided more specific information, such as RoBERTa's improved training procedure enhancing results on both GLUE and SQuAD, its GLUE leaderboard score (88.5), and achieving state-of-the-art on some tasks.
* **Review:**
    * Accuracy (After Improvement): Medium-High. While accurately acknowledging the limitation (no explicit numerical comparison in the source), the system extracted the most relevant available information, improving the detail of the answer due to enhanced context retrieval capabilities.

---
### Detailed Single & Multi-File Test Log & System Performance Review

#### Test File: `main.pdf` ("Sentiment Analysis using Bidirectional LSTM Network")

**Question 1:** What dataset was used for the research in 'Sentiment Analysis using Bidirectional LSTM Network'?
> **RAG System's Answer:** The Amazon Product Review dataset was used as the source of data for the research in 'Sentiment Analysis using Bidirectional LSTM Network'.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "The Amazon Product Review dataset served as the source of data for this research."

**Question 2:** How many product reviews were analyzed in this study?
> **RAG System's Answer:** The study analyzed 104,975 product reviews.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "Concretely, the analysis is performed on 104,975 product reviews reflecting users' attitudes toward mobile electronics products." and "It consists of 104975 reviews."

**Question 3:** What are the two categories the proposed model attempts to classify reviews into?
> **RAG System's Answer:** The proposed model attempts to classify reviews into two categories: positive and negative.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "The proposed model attempts to classify the reviews into two categories: positive and negative."

**Question 4:** Summarize the proposed methodology in 'Sentiment Analysis using Bidirectional LSTM Network'.
> **RAG System's Answer:** The proposed methodology in 'Sentiment Analysis using Bidirectional LSTM Network' involves employing a Bidirectional LSTM model to perform sentiment classification. The model consists of different layers, including an embedding layer, bidirectional LSTM layers, dense layers, and dropout layers. The embedding layer takes parameters such as batch size and vocabulary size as inputs. The bidirectional LSTM layers have 128 units and use the tanh activation function. The dense layers use the ReLU activation function and have different unit configurations. The dropout layers are used to prevent overfitting of the model. The model is trained to classify reviews into two categories: positive or negative. The performance of the model is then evaluated using metrics like accuracy, precision, recall, F1 score, specificity, and misclassification rate.
> **Review:**
> * **Accuracy:** Mostly correct, but can be more structured and precise according to the paper's flow.
> * **PDF Evidence:** The paper details the methodology in sections 3.1 ("Proposed Methodology") and 3.2 ("Procedure").
> * **Suggested Improved Summary:** "The proposed methodology described in main.pdf consists of the following stages: First, data is collected from the Amazon Product Reviews dataset. Since this raw data may contain noise and errors, it undergoes a pre-processing stage. This includes tokenization and case-folding of the review data. The processed data is then converted into word vectors using a text encoder. This data is divided into training and validation sets, and each review body is padded with 'zeros' at the end to ensure all reviews in a batch fit a standard length. Next, a Bidirectional LSTM (Bi-LSTM) network is constructed and trained to classify the reviews into two categories: positive or negative. Finally, performance evaluation metrics associated with the sentiment classifier (accuracy, precision, recall, F1 score, specificity, and misclassification rate) are computed. The model design comprises an embedding layer, two Bi-LSTM layers (each with 128 units and tanh activation function), three Dense layers (ReLU activation function), dropout layers, and an output layer with a single neuron. Binary cross-entropy is used as the loss function, compiled with the 'Adam' optimizer, and evaluation is based on accuracy."

**Question 5:** According to main.pdf, what is the main advantage of LSTM networks for sentiment analysis?
> **RAG System's Answer:** The main advantage of LSTM networks for sentiment analysis, as per the document, is its ability to handle long-term dependencies which is essential in understanding the context in sequential data like text. This makes it particularly suitable for tasks like sentiment analysis where the sequence and context of words can affect the sentiment conveyed.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "This model is capable of handling long-term dependencies by introducing memory into the model for making better predictions.". Also, "LSTM is a specific class of RNN that is well-suited to learn long term dependencies [10]."

---
#### Test File: `19967-pdf.pdf` ("Beauty and the Beast")

**Question 1:** How many sons and daughters did the merchant have in 'Beauty and the Beast'?
> **RAG System's Answer:** The merchant in 'Beauty and the Beast' had six sons and six daughters.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "As he had, however, six sons and six daughters..."

**Question 2:** What did the Beast say he would do if the merchant failed to keep his word?
> **RAG System's Answer:** The Beast said that if the merchant did not keep his word, he would die. He stated this after warning the merchant to remember his promise and return when the time is up.
> **Review:**
> * **Accuracy:** Partially Correct (interprets consequence as death).
> * **PDF Evidence:** "If neither of them is willing, you must come alone, after bidding them good-bye for ever, for then you will belong to me. And do not imagine that you can hide from me, for if you fail to keep your word I will come and fetch you!”
> * **Suggested Clarification:** The Beast stated the merchant would "belong to me" and that he would "come and fetch" him, which implies a severe consequence, though not explicitly "death" by the Beast's words.

**Question 3:** Summarize the merchant's misfortunes at the beginning of 'Beauty and the Beast'.
> **RAG System's Answer:** The merchant's misfortunes began when he was returning home and stopped to gather a rose for his daughter, Beauty, from a hedge of exquisite flowers. However, as he did this, a frightful Beast appeared. The Beast was very angry and accused the merchant of being ungrateful and stealing his flowers after he had allowed him to stay in his palace. Despite the merchant trying to explain his actions and his misfortunes, the Beast remained furious and threatened him with death.
> **Review:**
> * **Accuracy:** Incorrect focus. The question asks about misfortunes "at the beginning," which refers to his financial ruin before encountering the Beast.
> * **PDF Evidence:** "Their house caught fire and was speedily burnt to the ground... suddenly lost every ship he had upon the sea... his clerks... had proved unfaithful; and at last from great wealth he fell into the direst poverty."
> * **Suggested Improved Answer:** "At the beginning of 'Beauty and the Beast', the merchant's misfortunes included his house burning down, losing all his ships at sea through various calamities, and being cheated by his clerks, which led to him falling from great wealth into dire poverty."

**Question 4:** Describe the Beast's initial reaction when he found the merchant taking a rose.
> **RAG System's Answer:** When the Beast found the merchant taking a rose, his initial reaction was one of anger. He was very furious and confronted the merchant, saying in a terrible voice: "Who told you that you might gather my roses? Was it not enough that I allowed you to be in my palace and was kind to you? This is the way you show your gratitude, by stealing my flowers! But your insolence shall not go unpunished." The Beast then accused the merchant of being ungrateful and threatened him with punishment.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** The dialogue quoted is accurate from the text.

**Question 5:** Why did Beauty decide to go to the Beast's castle?
> **RAG System's Answer:** Beauty decided to go to the Beast's castle to keep her father's promise. She felt responsible for the misfortune that had befallen her family, as it was her request for a rose that led to her father's encounter with the Beast. As a result, she believed it was only just that she should be the one to suffer the consequences and thus decided to return to the Beast's castle with her father.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "But as I did the mischief it is only just that I should suffer for it. I will therefore go back with my father to keep his promise."

---
#### Test File: `2505.22680v1.pdf` ("Exploring Holography in Neuro-Vascular Dynamics")

**Question 1:** What is cerebral autoregulation?
> **RAG System's Answer:** Cerebral autoregulation refers to the brain's ability to maintain a constant level of cerebral blood flow despite changes in blood pressure. This process is known to function within a mean arterial pressure range of approximately 60-150 mmHg, during which flow velocity remains relatively stable. The mechanisms underlying cerebral autoregulation are complex and not entirely understood, with ongoing discussions regarding the role of sympathetic nervous activity. It is also suggested that there are other factors at play, such as astrocytes and neurovascular coupling, which adjust blood flow to meet the energy needs of activated neurons.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "Cerebral autoregulation is the brain's ability to preserve cerebral blood flow at a constant level despite changes in blood pressure [25,26]." Details on MAP range and complexity are also in the paper.

**Question 2:** Briefly explain the fluid/gravity duality mentioned in the abstract of 2505.22680v1.pdf.
> **RAG System's Answer:** The fluid/gravity duality mentioned in the document refers to the theoretical correspondence between a solution of Einstein’s equations near an asymptotically AdS black brane and the relativistic Navier-Stokes equations on the conformal boundary. This duality can be extended to non-relativistic hydrodynamics by adjusting the structure in the bulk. It is also suggested that Lifshitz and Schrödinger spacetimes can generate diffusive scaling symmetries of the incompressible Navier-Stokes equation and geometrize Galilean boosts and a conserved particle flow pattern, respectively. In a holography, this fluid/gravity dual serves as the bridge between the boundary’s Conformal Field Theory (CFT) and the black-brane. The validation of a fluid/gravity dual is seen as evidence for the existence of a holographic correspondence.
> **Review:**
> * **Accuracy:** Correct. A good summary of a complex topic based on the abstract and text.
> * **PDF Evidence:** The abstract states: "...interrogate its validity through the fluid/gravity duality—a correspondence linking hydrodynamic equations to gravitational spacetime metrics." The body further elaborates on this.

**Question 3:** What is the significance of the 'dial-a-delay' effect in Schrödinger holography for explaining neurovascular coupling?
> **RAG System's Answer:** The 'dial-a-delay' effect in Schrödinger holography is significant for explaining neurovascular coupling due to its ability to engineer a tunable signal delay. This delay can be produced independent of fluid viscosity or the initial wave-packet shape, making it potentially physiologically relevant. It provides a mechanism that could explain the delays in circulation times observed in cerebral models, which are vital for the complex communication between neurons, astrocytes, and cerebral vessels that adjusts blood flow to meet the energy needs of activated neurons. However, the exact translation of this effect to a cerebral model requires further investigation.
> **Review:**
> * **Accuracy:** Correct.
> * **PDF Evidence:** "This “dial-a-delay” effect—controlled geometrically operates independently of microscopic transport coefficients (v, ζ) or initial data." and "This shows that a translation to a cerebral model could also, in principle, produce delays in the range of circulation times, which makes it then physiologically relevant."

---
#### Test Files: `main.pdf` and `d572e43d0c120d59e81c228f2a17b3b05006.pdf`

**Question 1:** Compare the datasets used in 'Sentiment Analysis using Bidirectional LSTM Network' (main.pdf) and 'Text based Sentiment Analysis using LSTM' (d572e43d0c120d59e81c228f2a17b3b05006.pdf).
> **RAG System's Answer:** The document does not provide specific information about the datasets used in the studies 'Sentiment Analysis using Bidirectional LSTM Network' and 'Text based Sentiment Analysis using LSTM'. Therefore, a comparison cannot be made based on the provided text. (Query type: normal)
> **Review:**
> * **Accuracy:** Incorrect. Both PDFs specify their datasets.
> * **PDF Evidence `main.pdf`:** "The Amazon Product Review dataset served as the source of data for this research."
> * **PDF Evidence `d572e43d0c120d59e81c228f2a17b3b05006.pdf`:** "We are using IMDB movies review [6] and Amazon Product datasets used to train and validate our models."
> * **Suggested Improved Answer:** "'Sentiment Analysis using Bidirectional LSTM Network' (main.pdf) used the Amazon Product Review dataset, specifically the Mobile Electronics category. 'Text based Sentiment Analysis using LSTM' (d572e43d0c120d59e81c228f2a17b3b05006.pdf) utilized both the IMDB movie review dataset and Amazon Product datasets."

**Question 2:** What are the key differences in the LSTM architectures (e.g., layers, units) proposed or discussed in main.pdf and d572e43d0c120d59e81c228f2a17b3b05006.pdf, if detailed?
> **RAG System's Answer:** The document discusses about Long Short-Term Memory (LSTM) architectures, specifically the standard LSTM and the Bidirectional LSTM (Bi-LSTM). In the standard LSTM, it is mentioned that there are four layers that interact in a unique manner... Unfortunately, the document does not provide any details about the LSTM architectures discussed in the file named 'd572e43d0c120d59e81c228f2a17b3b05006.pdf'.
> **Review:**
> * **Accuracy:** Partially Incorrect. While the description of LSTM/Bi-LSTM from `main.pdf` might be generally okay, the claim that `d572e43d0c120d59e81c228f2a17b3b05006.pdf` provides no architectural details is false.
> * **PDF Evidence `main.pdf`:** Details its Bi-LSTM model with an embedding layer, 2 Bi-LSTM layers (128 units, tanh), 3 dense layers (ReLU), dropout, and an output layer.
> * **PDF Evidence `d572e43d0c120d59e81c228f2a17b3b05006.pdf`:** Provides a model summary table: "embedding 1 (Embedding)", "lstm_1 (LSTM)" (Output Shape (None, 128)), "dense 1 (Dense)" (Output Shape (None, 5)). It also mentions, "Each word is represented with an embedding vector of size 100."
> * **Suggested Improved Answer:** "'Sentiment Analysis using Bidirectional LSTM Network' (main.pdf) proposes a Bi-LSTM model with an embedding layer, two Bi-LSTM layers (128 units each, tanh activation), three dense layers (ReLU), dropout layers, and a single neuron output layer. 'Text based Sentiment Analysis using LSTM' (d572e43d0c120d59e81c228f2a17b3b05006.pdf) details an LSTM model with an embedding layer (embedding vector size 100), one LSTM layer (128 units), and a dense layer with 5 output units. Key differences include the use of Bi-LSTM versus standard LSTM, the number of LSTM and dense layers, and the output layer size, suggesting different classification tasks (binary in main.pdf vs. potentially multi-class in d572e43d0c120d59e81c228f2a17b3b05006.pdf)."

**Question 3:** Based on main.pdf and d572e43d0c120d59e81c228f2a17b3b05006.pdf, provide a combined overview of why LSTMs are suitable for sentiment analysis.
> **RAG System's Answer:** Long Short-Term Memory (LSTM) models are suitable for sentiment analysis for several reasons. Firstly, LSTM is adept at handling long-term dependencies... Secondly, LSTM networks can process a substantial amount of data... Additionally, the use of a Bidirectional LSTM allows the model to have access to past and future input features...
> **Review:**
> * **Accuracy:** Good. The RAG system provided a reasonable combined overview based on the general strengths of LSTMs mentioned in both papers.
> * **PDF Evidence:** Both papers support these points: `main.pdf` emphasizes Bi-LSTM's capability for long-term dependencies and handling past/future context. `d572e43d0c120d59e81c228f2a17b3b05006.pdf` highlights LSTMs' design for long-term dependency problems and success in sentiment classification.

---
#### Test Files: `main.pdf` (Bi-LSTM), `Analyzing...BERT....pdf`, and `W19-6120.pdf` (BERT for ABSA)

**Question 1:** Compare the core NLP task addressed in main.pdf (Bi-LSTM) versus W19-6120.pdf (BERT for ABSA).
> **RAG System's Answer:** The document does not provide explicit information about the core NLP task addressed in main.pdf (Bi-LSTM). However, it discusses in detail the task addressed in W19-6120.pdf (BERT for ABSA)... Due to a lack of information about the Bi-LSTM approach, a direct comparison cannot be made.
> **Review:**
> * **Accuracy:** Incorrect. `main.pdf` clearly states its task.
> * **PDF Evidence `main.pdf`:** Title is "Sentiment Analysis using Bidirectional LSTM Network". Abstract states, "Sentiment analysis is primarily concerned with the classification and prediction of users' thoughts and emotions from these reviews."
> * **PDF Evidence `W19-6120.pdf`:** Title is "Aspect-Based Sentiment Analysis Using BERT". Abstract states, "Aspect-based sentiment analysis (ABSA) is a more complex task that consists in identifying both sentiments and aspects."
> * **Suggested Improved Answer:** "'Sentiment Analysis using Bidirectional LSTM Network' (main.pdf) addresses general sentiment analysis, aiming to classify the overall emotional tone (e.g., positive/negative) of product reviews. In contrast, 'Aspect-Based Sentiment Analysis Using BERT' (W19-6120.pdf) focuses on Aspect-Based Sentiment Analysis (ABSA), a more granular task that identifies sentiments directed towards specific entities or aspects within a text. So, `main.pdf` determines overall review sentiment, while `W19-6120.pdf` identifies sentiment for specific features mentioned."

**Question 2:** Contrast the evaluation metrics focused on in main.pdf (Bi-LSTM) with those used for BERT models in 'Analyzing...BERT....pdf'.
> **RAG System's Answer:** The document does not provide information on the evaluation metrics focused on in main.pdf (Bi-LSTM). For the BERT models, the evaluation metrics mentioned in the document include training accuracy, validation accuracy, and testing accuracy... The document does not provide a contrast...
> **Review:**
> * **Accuracy:** Incorrect. `main.pdf` specifies its evaluation metrics.
> * **PDF Evidence `main.pdf`:** "...performance evaluation metrics associated with sentiment classifier, such asaccuracy, precision, recall, F1 score, specificity and misclassification rate, are computed." Also Table 2 lists these.
> * **PDF Evidence `Analyzing...BERT....pdf`:** "...compared using the accuracy as the performance evaluation matrix." Table I and II show "Training Accuracy", "Validation Accuracy", "Testing Accuracy".
> * **Suggested Improved Answer:** "'Sentiment Analysis using Bidirectional LSTM Network' (main.pdf) uses accuracy, precision, recall, F1 score, specificity, and misclassification rate. 'Analyzing the Performance of Sentiment Analysis using BERT, DistilBERT, and RoBERTa.pdf' primarily uses accuracy (training, validation, and testing) to compare its models. Thus, `main.pdf` uses a broader set of classification metrics compared to the primary focus on different forms of accuracy in `Analyzing...BERT....pdf`."

---


## 🚀 Future Development & Enhancements

Our vision for DocInsight involves continuous improvement in performance, accuracy, user experience, and feature set. Key areas for future development include:

**1. Core RAG Pipeline Optimization (High Priority):**
  - **Advanced Prompt Engineering & Context Selection:**
    - Dynamically control and optimize prompt length based on query type, document type, and available context.
    - Implement and A/B test hybrid chunk selection strategies, combining keyword-based filtering with enhanced vector-based re-ranking for optimal context retrieval.
    - Explore techniques for prioritizing chunks containing highlighted text or other explicit markers of importance within documents.
  - **Robust Handling of Multi-Document Reasoning:**
    - Further develop and rigorously test the system's ability to perform complex reasoning and synthesis across multiple (2-3+) specified documents.
    - Refine prompt construction for nuanced multi-document queries, including indirect questions, comparative analysis requiring inference, and hybrid (e.g., summarize then compare) question types.

**2. Performance & Scalability:**
  - **Scalability for Large Document Sets:**
    - Optimize indexing, chunking, and memory management to efficiently support significantly larger document collections (e.g., 50+ PDFs) without performance degradation.
    - Investigate and implement strategies such as asynchronous I/O for parallel index operations, transitioning to a global FAISS index with metadata filtering, and memory-mapped file access for vector storage.

**3. User Experience (UI/UX) & Functionality:**
  - **Improved Frontend Interface:**
    - Enhance the document selection mechanism in the Streamlit UI (e.g., multi-select dropdowns with search, checkboxes).
    - Implement a file chunk preview feature.
    - Visually indicate the classified query type (`summary`, `comparison`, `normal`) to the user.
  - **Multi-language Support:**
    - Extend semantic search and question-answering capabilities to non-English documents, with initial support planned for Korean and French.

**4. System Operations & Maintainability:**
  - **Enhanced Logging and Monitoring:**
    - Transition from `print()` statements to a structured logging system (e.g., Python's `logging` module) for improved debugging and operational monitoring.
    - Integrate monitoring for LLM call costs, API response times, and token usage.

**(Optional: Section for Recently Completed Major Milestones - if you want to highlight progress from the old "Planned Improvements")**
  - **Recently Implemented:**
    - Semantic Query Classification using sentence embeddings.
    - Original Context Preview for full traceability.
    - Targeted QA with user-selectable file filtering.
    - Advanced Chunking Strategies (paragraph-based, deduplication, diversity, Head-Tail, document-type specific, section-aware, and re-ranking).
    - Initial Debugging & Explainability Tools.






