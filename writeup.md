### Time Used
- Establish Note Taking App (Around 2 hours)
- Migrate SQLite to Supabase (Around 1.5 hours)
- Migrate GitHub to Vercel (Around 5.5 hours)
#### **Total 9 hours**
<br/>

### Establish Note Taking App Event

**GitHub Establishment**
- Established NoteTaker App (Repository: COMP5241-2526Sem1/note-taking-app-updated-keith-flma).
- Reviewed class zoom video and notes.
- Established Note Taking App.
- Added note relocation feature.
- Added API key and LLM.
- Added AI Translate, Extract Structure and Note Generation features.

**Migration to Supabase**
- Used GitHub account to create Supabase account.
- Checked Connection String (Dashboard -> Connect).
- Checked anon/public and service_role API keys (Project Settings -> Legacy API Keys).
- Enabled SSL (Project Settings -> Enforce SSL on incoming connections).
- In GitHub, the app could not connect to Supabase and migration failed. Finally found that the reason was IPv6 issue. AI helped to solve the problem.
- After the connection was established, there was another error. Finally found that the tables were not created in database. The problem was solved after tables are created.

**Migration to Vercel**
- Used GitHub account to create Vercal account and added a new project.
- AI helped to deploy app to Vercel. vercel.json was created.
- After deployment to Vercel completed, AI suggested to "Import" Git Repository in Vercel. But my repository "COMP5241-2526Sem1/note-taking-app-updated-keith-flma" in Vercel was not visable.
- AI found the reason was my repository which was not “Public”.
- AI replied whether my repository needs to make it public:
    - When the repository needs public: Free Vercel plan, Vercel GitHub App not installed and organization restrictions.
    - When the repository can keep private: Vercel Pro plan, GitHub App properly installed and Personal repository
- Checked GitHub (Settings -> General -> Danger Zone -> Change repository visibility) in invisibility, but it cannot be changed to visibility (button grey).  The reason was the organization restriction.
- AI suggested Manual Fork of my repository via GitHub (Code -> Fork -> Create a new fork). The fork “COMP5241-2526Sem1/note-taking-app-updated-keith-flma1” was created which could Import to Vercel.
- But there were errors to deploy the GitHub fork to Vercel. The reason was the fork which was also “Private” and could not be changed to “Public” because of inherited restrictions from the original organization repository.
- AI tried several methods but the Vercel still had errors during deployment. AI suggested changing Vercel from free to Pro trial account. 
- AI tried to use Vercel CLI directly (bypasses GitHub entirely) to deploy repository “COMP5241-2526Sem1/note-taking-app-updated-keith-flma” in Vercel and the manual fork was deleted.
- The deployment still had errors.
- I found that the organization has another repository “COMP5241-2526Sem1/note-taking-app-keith-flma” which can change to “Public”.

**Manual Migration of Repository**
- Copied the necessary files from repository “COMP5241-2526Sem1/note-taking-app-updated-keith-flma” to repository “COMP5241-2526Sem1/note-taking-app-keith-flma”
- AI helped to double check and fix bugs.
2nd Vercel Deployment
- AI helped to deploy repository “COMP5241-2526Sem1/note-taking-app-keith-flma” to Vercel. But app can be produced to Vercel but the webpage cannot be displayed.
- Finally found that is Python version of GitHub incompatible problem. The webpage can be displayed after Python upgraded.
- But the app cannot connect to Supabase.

**2nd Migration to Supabase**
- Finally found that the reason was Vercel could not support IPv6.
- Changed the connection to “Transaction Pooler” with port 6543 for IPv4 support (Connection -> Connection String -> Transaction Pooler)
- After update the link in Vercel, the app can use the database of Supabase.
- But the app had errors for the translation using “Generate Note” and “Translation” button.

**Fix Translation Feature**
- Add the GITHUB_TOKEN to Vercel (Project Settings -> Environments -> Environment Variables)
- Used the existing or generate a new GitHub GPT 4.1 mini API key that still cannot use the translate function.
- AI suggested to use OpenAI API key, but Hong Kong cannot use it due to regional restrictions.
- AI suggested to use Microsoft Translator API and Google Cloud Translation API, but those APIs need to register and add some information/configuration before use.
- After searching various solutions, finally decided to use Hagging Face which only requires registration to access API.
- After AI helped to modified the codes and the translation feature can be used.

**NoteTaker Deployment to Web**
- AI help to double check all files, the app was finally deployed to the website and all features were normally.
 


