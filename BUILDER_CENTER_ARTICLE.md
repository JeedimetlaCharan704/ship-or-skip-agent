# ShipOrSkip AI: The 3 AM Hackathon Sanity & MVP Scope Coach
**Tag:** `#agents` `#AWS` `#AmazonBedrock` `#AWSLambda` `#challenge`

---

## What and Who

Have you ever witnessed a hackathon team at 3:00 AM on Sunday morning, staring at a broken OAuth flow or debugging an unresponsive Kubernetes ingress while the countdown timer shows four hours until submission? 

Every seasoned hacker has been there. Great ideas do not die at hackathons because the developers lack talent; they die because of **scope creep**. In the heat of the opening ceremony, teams commit to building multi-tenant SaaS platforms, payment checkouts, complex multi-agent swarms, and bespoke mobile apps. By the final sprint, they have six unfinished screens, zero working end-to-end user journeys, and nothing demonstrable to show the judges.

**ShipOrSkip AI** is an intelligent scope-coaching agent designed specifically for tired hackathon teams, student builders, and solo weekend sprint developers. 

Instead of generating more code or adding more ideas, ShipOrSkip does the opposite: it aggressively protects your submission deadline. You provide your project name, your remaining hours, your tech stack, and your raw feature wish-list. In return, the agent delivers:
1. **Feasibility Verdict & Trust Score (0–100%)**: An instant calculation of whether your scope realistically fits your remaining hours.
2. **The Fatal Rabbit Hole**: Identification of the exact single dependency or architectural distraction (e.g., custom user registration, real payment transactions, or training models from scratch) that threatens to swallow your entire night.
3. **The "Golden Path" One-Feature MVP**: A distilled, laser-focused definition of the single input-to-output loop that will win over judges.
4. **The Countdown Sprint Roadmap**: A strict three-phase timeboxed plan allocating dedicated time for core business logic, single-screen UI integration, and mandatory demo video recording.
5. **The Scope Cut List**: A concrete checklist of secondary features to drop or mock with static JSON fixtures.

---

## How I Built It

To keep the agent responsive, lightweight, and deployable within a weekend timeline, I built a serverless, decoupled architecture utilizing Amazon Web Services.

### Architecture Overview
1. **Frontend Interface:** Built with a lightweight, responsive single-page web interface using Tailwind CSS and vanilla JavaScript. It includes quick-preset triggers, an intuitive remaining-hours countdown slider, and an interactive persona selector.
2. **Backend Engine:** Implemented with Python 3.12 and Flask for local execution, packaged with a serverless AWS Lambda handler (`lambda_function.py`) compatible with AWS Lambda Function URLs or Amazon API Gateway HTTP APIs.
3. **Foundation Model Reasoning with Amazon Bedrock:** The agent relies on **Amazon Bedrock** invoking the **Amazon Nova Micro** model (`amazon.nova-micro-v1:0`). Nova Micro provides the perfect balance of sub-second inference latency, ultra-low cost, and strict adherence to structured JSON schemas.
4. **Security & Identity:** IAM execution roles scoped strictly to the `bedrock:InvokeModel` action for the Nova Micro resource ARN, eliminating hardcoded credentials, secret leaks, or client-side API key exposures.
5. **Deterministic Heuristic Safeguard:** To adhere to production agent reliability principles, the agent incorporates a built-in deterministic heuristic scoring engine. If AWS credentials, quotas, or network timeouts occur, the agent seamlessly falls back to the heuristic rubric, ensuring 100% uptime with zero uncaught exceptions.

### System Prompt & Persona Engineering
The foundation of the agent is a structured system prompt that instructs the Bedrock model to act as an uncompromising hackathon mentor. The prompt encodes common hackathon failure modes—such as unmocked third-party APIs, authentication rabbit holes, and over-engineered infrastructure—and forces the model to output validated JSON containing clear quantitative metrics and qualitative action items.

---

## The Delightful Detail

A tool designed for high-stress deadline environments is only useful if it actually feels enjoyable and reassuring to interact with. For ShipOrSkip AI, I focused on three specific delightful details:

### 1. The Adaptive Coach Persona Slider
Builders experience different psychological states throughout a hackathon. To meet them where they are, ShipOrSkip provides three distinct persona modes:
* **🌱 Senior Mentor (Supportive Peer):** Warm, calming, and empathetic. When you have four hours left, it reassures you: *"Take a breath. The judges don't need five broken tabs; they just need to see your core magic work once without a hiccup. Cut the noise and protect your sleep."*
* **📐 Tech Lead (Pragmatic Architect):** Crisp, objective, and architectural. Focuses on interface contracts, hardcoded JSON mocks, and freezing requirements.
* **🔥 3 AM Judge (Tough Love):** Witty, blunt, and hilarious. Calls out over-engineered fluff with punchy realism: *"If you try to deploy a multi-agent Kubernetes swarm in four hours, your laptop will catch fire and you will be pitching empty slides. Build the single mock screen now."*

### 2. Never Leaving the Builder Stuck
Nothing frustrates a developer under deadline more than a blank loading spinner, a cryptic CORS error, or an unhandled JSON parse exception. ShipOrSkip features live health state indicators and automatic failover to the local deterministic rubric with amber notification badges. The builder *always* walks away with an actionable sprint plan.

### 3. One-Click Team Sync
Hackathon developers work in team chats (Slack, Discord, WhatsApp). With a single click, the "Copy for Team Chat" button extracts the assessment, verdict, fatal trap, and MVP path into a markdown-formatted snippet ready to paste straight to teammates.

### How I Know It Worked
I tested the agent across three realistic scenarios:
1. **The Overkill Swarm (4 hours left):** Inputting a crypto trading swarm with 5 LangChain agents, Kubernetes, and smart contracts. The agent correctly scored it 15/100 (SINK), flagged Kubernetes deployment as the fatal rabbit hole, and prescribed a single-screen mock interface.
2. **The 3 AM Panic Pivot (6 hours left):** Inputting a medical history summarizer with Stripe billing. The agent flagged payment checkout as dead weight and instructed the builder to hardcode a mock patient file.
3. **The Clean Golden Path (24 hours left):** Inputting a focused receipt-splitter app. The agent scored it 80/100 (SHIP), validating the scope and urging the team to freeze features early and record a high-quality video demo.

In every case, the persona stayed authentic, the recommendations were immediately actionable, and testing took under five seconds.

---

## Proof It Works

* **Live Application:** [https://ship-or-skip-agent.vercel.app](https://ship-or-skip-agent.vercel.app)
* **GitHub Repository:** [https://github.com/JeedimetlaCharan704/ship-or-skip-agent](https://github.com/JeedimetlaCharan704/ship-or-skip-agent)
* **Demonstration Walkthrough:**
  1. Open the application dashboard and review the preloaded presets ("🔥 4 Hours Left: 3 AM Panic", "🤖 Over-Engineered Multi-Agent", "✨ Clean 1-Feature Flow").
  2. Adjust the countdown slider to your remaining hackathon hours and select your preferred Coach Persona.
  3. Click **"Analyze Scope & Sanity Check"**.
  4. View the instant feasibility badge, the fatal rabbit hole warning, the one-feature MVP definition, and the timeboxed three-phase sprint roadmap.
  5. Hit **"Copy for Team Chat"** to synchronize your team's build priorities.

---

## What I Learned and What's Next

Building ShipOrSkip AI reinforced a critical truth about agentic engineering: **a great AI agent is not measured by how complex its workflow is, but by how much clarity it creates for the human user.**

By constraining the model to output a single golden path, eliminating technical rabbit holes, and infusing an empathetic, entertaining personality, the agent turns deadline panic into focused execution.

Next steps for ShipOrSkip include adding direct GitHub repository scanning via Amazon Bedrock Knowledge Bases to automatically detect uncommitted code bloat, and integrating Amazon Polly to deliver voice-guided 3 AM pep talks.

Remember: *Demo beats perfection. Ship your MVP!*

---
#agents #AWS #AmazonBedrock #AWSLambda #Hackathon
