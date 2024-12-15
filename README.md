# VulnGuard
> V1 maybe?

## Description

As GitHub gets increasingly utilised by developers, there is a growing probability of receiving commits from ill-minded users with malicious intentions. As such, developers are required to constantly review pull requests which requires a lot of manual work. Therefore, we decided to come up with an AI embedded code checker that checks for potential vulnerabilities and creating automated test cases.

## Features

- Vulnerability Analysis
  - Generates an analysis report of new commitments to a repository in less than 10 minutes.
- Automated Test Case Generation
  - Automatically generates test cases to prove that suggested changes work as intended.

## QNA

**Q: Who's the target audience?**

A: Open source developers.

**Q: How does it work/help?**

A: It reviews pull requests by flagging out potential vulnerabilities by checking if the new code added aligns with it's said description. It also automatically generates test cases through finding the dependency functions. This reduces the workload on open source developers as it simplifies their code reviewing process. 

**Q: What makes us special?**

A: Although there are quite a few code scanners in the market itself all of them employ static code analysis to flag out potential vulnerabilities. However, attackers with specially crafted malicious inputs can find ways to bypass the static analysis. Our tool utilises LLMs to infer the intent of the new code allowing it to catch a wide range of malicious inputs.

**Q: Limitations?**

A: As the code is being analysed through API calls through OpenAI, tokens limits imposed by them severely restrict the size of the code base analysed. As such, VulnGuard is currently unable to be integrated in huge repositories, but possible developments include migrating to local LLM to remove this limitation.
