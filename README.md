# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

This system covers real student experiences with tech internships, collected from 
Reddit communities (r/csMajors, r/cscareerquestions). It includes first-hand accounts 
of FAANG and startup internships, compensation data, remote vs. in-person comparisons, 
red flags to watch for, and advice on landing a first internship.

This knowledge is valuable because it doesn't exist in any structured, searchable 
format through official channels — it's scattered across thousands of threads and 
comments. A student trying to find out what WLB is actually like at Google has no 
way to get a consolidated answer without manually reading dozens of posts.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/csMajors | Reddit thread | https://www.reddit.com/r/csMajors/comments/1ic6vxn/google_software_engineer_internship_2025/ |
| 2 | r/csMajors | Reddit thread | https://www.reddit.com/r/csMajors/comments/1t7j0kf/former_amazon_sde_interns_how_much_value_did_the/ |
| 3 | r/csMajors + r/cscareerquestions | Reddit threads | https://www.reddit.com/r/csMajors/comments/1lfhutc/think_twice_before_you_work_for_any_startup/ |
| 4 | r/csMajors | Reddit thread | https://www.reddit.com/r/csMajors/comments/1nzx3l9/genuinely_how_are_you_supposed_to_get_your_first/ |
| 5 | r/csMajors | Reddit thread | https://www.reddit.com/r/csMajors/comments/155ur6y/what_i_learned_from_my_internship_i_dont_want_to/ |
| 6 | r/csMajors + r/cscareerquestions | Reddit threads | https://www.reddit.com/r/cscareerquestions/comments/1pnwh5n/official_salary_sharing_thread_for_new_grads/ |
| 7 | r/csMajors | Reddit thread | https://www.reddit.com/r/csMajors/comments/13nzjrb/interns_is_your_internship_remote_or_in_person/ |
| 8 | r/cscareerquestions + r/csMajors | Reddit threads | https://www.reddit.com/r/cscareerquestions/comments/r78kvz/got_hired_with_zero_experience/ |
| 9 | r/cscareerquestions | Reddit thread | https://www.reddit.com/r/cscareerquestions/comments/8zw6bw/what_questions_do_you_ask_the_company_before_you/ |
| 10 | r/csMajors + r/cscareerquestions | Reddit threads | https://www.reddit.com/r/csMajors/comments/qfr7gq/what_red_flags_do_you_notice_when_you_look_at/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 50 characters

**Why these choices fit your documents:**
The documents are Reddit threads made up mostly of short user comments (1–4 sentences 
each). Chunking by paragraph doesn't work well here because many "paragraphs" are 
just one sentence — not enough context to embed meaningfully. 500 characters fits a 
typical Reddit comment almost perfectly. Smaller than that and you get mid-sentence 
fragments. Larger and you start merging opinions from completely different users into 
one chunk, which hurts retrieval precision. The 50-character overlap handles the 
longer posts where a single comment spans multiple chunks, making sure a key idea 
near a boundary doesn't get lost.

**Final chunk count:** 207 chunks across 10 documents

**Sample chunks:**

**Chunk 1** (01_google_internship.txt):
> "Recently finished an internship at Google and it was a bad experience ngl. Team had 
shitty WLB and office politics. People constantly messaging each other well after work 
hours. They wouldn't even keep it subtle, my boss would directly ping people at 8, 9PM"

**Chunk 2** (06_internship_salary_compensation.txt):
> "$11/hour, at some tiny no-name company no one has heard of. Got it as a rising senior. 
It was the only internship on my resume when I was searching for new grad roles. I 
graduated into a SWE job making about $70k."

**Chunk 3** (10_red_flags_internship.txt):
> "We are a family. [453 upvotes] u/namonite: Can't turn your back on family. [100 upvotes] 
u/consensualwisdom: Work hard, play hard. [257 upvotes]"

**Chunk 4** (03_startup_vs_bigtech.txt):
> "Do not have a clear project in mind, always talking about abstract things that are 
impossible to understand. Do not give you a contract to sign, and the contract has 
absolutely no details on code ownership."

**Chunk 5** (07_remote_vs_inperson_internship.txt):
> "I'm mentoring an intern this summer. He has to come in but the entire team is remote. 
The absolute WORST of both worlds. This was me last summer — sitting in traffic only 
to arrive at an almost empty office."

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers — runs locally, no API 
key needed, no rate limits. Good fit for English-only opinion text like Reddit comments.

**Production tradeoff reflection:** For a real deployment I'd think about a few things. 
Context length matters — all-MiniLM-L6-v2 has a 256-token limit, which is fine for 
short Reddit comments but would miss content in longer chunks. If the corpus went 
multilingual (say, Spanish-speaking students sharing internship experiences) I'd 
switch to something like multilingual-e5. For better accuracy on domain-specific 
text, a hosted API model like OpenAI's text-embedding-3-small trades local control 
for higher quality embeddings — worth it if the use case is production-grade. For 
this project, local + free was the right call.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
You are a helpful assistant answering questions about tech internship experiences.
Answer using ONLY the information provided in the documents below. 
Do not use any outside knowledge or make assumptions beyond what is in the text.
If the documents do not contain enough information to answer the question, say exactly:
"I don't have enough information in my documents to answer that."
Always cite your sources by mentioning the document name (e.g. "According to 01_google_internship.txt...").
Keep your answer concise and focused on what the documents actually say.

**How source attribution is surfaced in the response:**
Source attribution works two ways. First, the system prompt instructs the LLM to 
cite document names inline in its answer (e.g. "According to 01_google_internship.txt..."). 
Second, the retrieved source filenames are collected programmatically from the 
ChromaDB results and displayed separately in the Sources panel of the UI — so even 
if the model forgets to cite inline, the sources are always visible to the user.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about work-life balance at Google internships? | Poor WLB reported — late night pings, 60+ hour weeks, team-dependent experience | Cited 01_google_internship.txt, mentioned boss pinging at 8-9PM, noted experience varies by team | Partially relevant — pulled 10_red_flags and 05_technical_learnings alongside the right doc | Accurate |
| 2 | How much do FAANG interns typically make per month? | $7,500–$12,000/month depending on company and role | Only surfaced one data point ($7.5k from one comment) — missed the richer salary thread data | Partially relevant — pulled 01_google instead of focusing on 06_salary | Partially accurate |
| 3 | What are red flags in internship job descriptions? | "We are a family", fast-paced, unpaid, no culture info, rockstar developer | Correctly listed phrases like "We are a family", "Work hard play hard", unpaid, no culture mention | Relevant — 10_red_flags was top result | Accurate |
| 4 | What do students recommend for getting a first internship with no experience? | Apply anyway, use projects and clubs, network, try smaller companies | Pulled advice from 04 and 08, mentioned startups and networking but missed some key tips | Relevant | Partially accurate |
| 5 | What are the tradeoffs between remote and in-person internships? | In-person better for networking, remote needs intentional relationship-building | Correctly captured both sides from 07_remote — commute tradeoff, going under the radar risk | Relevant — 07_remote was the only source | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"How much do FAANG interns typically make per month?"

**What the system returned:**
Only one data point — $7.5k/month from a single comment in 06_internship_salary_compensation.txt. 
The document actually has a much richer set of salary numbers (Amazon $10,500/month, 
Microsoft $7,500/month, various hourly rates), but the system missed most of them.

**Root cause (tied to a specific pipeline stage):**
This is a retrieval problem. The salary document has a lot of structured data — 
usernames, dollar amounts, company names — packed into short comment-sized chunks. 
At 500 characters, several chunks ended up being just a list of numbers without 
enough surrounding context for the embedding to recognize them as "FAANG salary data." 
The query "how much do FAANG interns make" didn't match those number-heavy chunks 
semantically because the embedding model weighted the narrative context more than 
the raw figures.

**What you would change to fix it:**
Try larger chunks (800-1000 characters) for the salary document specifically, so 
each chunk includes both the company name and the compensation number together. 
Metadata filtering by document topic would also help — letting users specify 
"salary" as a filter to bias retrieval toward 06_internship_salary_compensation.txt.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Writing the chunking strategy in planning.md before touching any code forced me to 
actually think about what my documents looked like structurally. When I sat down to 
implement chunk_text(), I already knew I wanted 500 characters with 50 overlap and 
why — so instead of just copying a generic chunking function, I had something 
specific to implement and verify against. The sample chunk inspection step made a 
lot more sense because I had a mental model of what "good" looked like beforehand.

**One way your implementation diverged from the spec, and why:**
The spec didn't anticipate the ChromaDB distance metric issue. I originally planned 
to use ChromaDB's default settings, but during retrieval testing the distance scores 
were all above 1.0 — which made it impossible to judge relevance. I had to switch 
from the default L2 (Euclidean) distance to cosine similarity by adding 
`metadata={"hnsw:space": "cosine"}` to the collection. That wasn't in the spec 
because I didn't know it would be a problem until I saw the actual numbers.
Pégalo y nos queda solo AI Usage — la última sección.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My Chunking Strategy and Documents sections from planning.md, 
plus the pipeline diagram. I asked Claude to implement ingest.py — a script that 
loads all .txt files from documents/, strips the SOURCE/TOPIC header lines, and 
returns chunks with source filename as metadata.
- *What it produced:* A working ingest.py with clean_text(), chunk_text(), and 
load_documents() functions, all heavily commented.
- *What I changed or overrode:* The generated code worked as-is, but I asked Claude 
to over-comment every line because I wanted to actually understand what was happening 
at each step — not just run code I couldn't explain.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md and the 
architecture diagram. I asked Claude to implement retriever.py with embed_and_store() 
using all-MiniLM-L6-v2 and ChromaDB, and a retrieve() function returning top-5 chunks 
with distance scores and source metadata.
- *What it produced:* A working retriever.py. Initial distance scores were all above 
1.0 which seemed wrong.
- *What I changed or overrode:* I flagged the high distance scores and Claude diagnosed 
the issue — ChromaDB was using L2 distance by default instead of cosine similarity. 
I updated the collection initialization to add `metadata={"hnsw:space": "cosine"}` 
which brought scores down to a reasonable range (0.38–0.55).
