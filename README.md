# TaaS — Taste as a Service

A film recommendation tool that captures aesthetic and cinematic sensibility through how someone talks about films they love, rather than relying on a user picking from a list of preset options.

## Project Description

Most film recommenders match on genre tags or collaborative filtering. For instance, some streaming services suggest content using logic like, *"people who watched X also watched Y"*. This recommendation approach can work for genre, but can be limited in capturing what an individual user actually means when they say they love a film: the texture, the pacing, the emotional register, the visual sensibility or what a film feels like to them.

In TaaS, the user describes a few films they love and why. An LLM reads the user's prose, the films named and the language used to describe them, to infer the preferred aesthetic sensibility of the user. The model then returns four recommendations grounded in that sensibility, providing a reasoning that ties each film pick back to what was inferred.

The taste profile is shown to the user and not hidden inside the recommendation logic. The system's reading of the user becomes a real output, which is what makes this different from a typical recommender.

## Why TaaS Was Built

I wanted to explore whether an LLM can capture aesthetic taste from prose and a way to capture feedback on the recommendations to evaluate whether the LLM is actually reading user input or just sounding like it.

## How It Works

### Stack

- **Python 3.14**
- **Streamlit** — UI
- **Anthropic Claude (Sonnet 4.5)** — inference
- **python-dotenv** — local API key handling

### Project Structure

```
taas-mvp/
├── app.py            # Streamlit UI, API call, parsing, rendering
├── prompts.py        # System prompt and user prompt files
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The prompt logic is separated into own file from the app logic to make the app code easier to understand. I iterated on the prompt to test the different user type prompts to the recommendation results of the LLM application. 

### Prompt Architecture

Prompt design decisions for the model:

1) **One API call instead of two.**
My first thought was to split this into two API calls, one to extract the taste profile, a second to generate recommendations from it. However, this would have made the app twice as slow and twice as expensive without making the output noticeably better, so I went with a single prompt that asks for both at once.

2) **The model evaluates for prose rather than labels.**
The model could have returned a list of taste tags (*"slow-paced, dialogue-light, atmospheric"*), however, this models classification that is present in other existing recommenders. Instead, the model asks users for 3–5 sentences of prose in second person ("You respond to films that…") so the output provides a more accurate reading of the user rather than relying on labels.

3) **Putting the profile before the recommendations.**
When asking the model directly for recommendations, the explanations for each pick explained closest matches of what was similar without explaining why. When I changed the prompt to require the model to write out the taste profile first the reasoning for each film became more intentional. 

This allowed each recommendation to evaluate picks based on specific preferences in the profile. The system prompt also explicitly tells the model what not to do such as to not match genres, not use shared-director logic, and to not lead with "people who watched X also watched Y." Providing constraints for what the model should avoid mattered as much as telling it what to do for choosing better film recommendations.

## Other Design Decisions

1) **Using Streamlit for a MVP.**
Streamlit handles the UI for a small project focused on the interaction model rather than frontend design.

2) **Choosing the Sonnet model.**
 Sonnet 4.5 was chosen to handle prose generation at a reasonable cost compared to more expensive models such as Opus.

### Fixing Parsing Issues

The first time the app was tested, it crashed because the model's response wasn't valid JSON, even though the prompt asked for JSON. I added a parser that grabs everything between the first `{` and the last `}` in the response, so any extra content around the JSON gets ignored. I also tried prefilling, where the API call starts the model's response with `{` so the model has to continue from there as JSON. Overall, the LLM output needed a layer of handling, since format instructions don't always get followed.

## Test Example

**User Input:**

> *I love Interstellar, the soundtrack and music composition guide the intensity and anticipation throughout the film. And Finding Nemo, for the universal themes of coming of age and the creative direction of using sea creatures to convey messages about working with one another, community, family, and resilience. I also love the soundtrack in Finding Nemo that conveys emotions and thematic elements.*

**Inferred taste profile:**

> *You respond to films that use music as an emotional architecture — where the score doesn't just accompany but actively shapes how you experience tension, wonder, and resolution. You're drawn to stories that embed profound human themes (family bonds, resilience, interdependence) within imaginative worlds that feel both expansive and intimate. The sensibility you gravitate toward is earnest rather than cynical, using spectacle and scale not for their own sake but to amplify emotional stakes.*

**Recommendations:**

- **Arrival** (2016, dir. Denis Villeneuve) — *Jóhann Jóhannsson's score functions exactly as you described — it builds anticipation and emotional intensity while being inseparable from the film's meditative pacing. Like your preferred films, it embeds deeply human themes within a speculative framework, trusting music and visual language to carry weight that dialogue cannot.*
- **The Red Turtle** (2016, dir. Michaël Dudok de Wit) — *A dialogue-free animated film that uses Laurent Perez del Mar's score as its primary emotional language, guiding you through themes of family, resilience, and acceptance with the same earnest sincerity you found in Finding Nemo.*
- **The Fountain** (2006, dir. Darren Aronofsky) — *Clint Mansell's score is the gravitational center, orchestrating anticipation and emotional release across three interconnected timelines. The film treats grand themes with sincerity, allowing the soundtrack to guide you through emotional terrain that resists easy articulation.*
- **Song of the Sea** (2014, dir. Tomm Moore) — *Bruno Coulais and Kíla's score weaves Irish folk traditions into the emotional fabric of the film, creating the same symbiosis between music and storytelling you prize. It shares Finding Nemo's approach of embedding universal themes within a richly imagined world.*

A genre engine, with film inputs such as Interstellar and Finding Nemo, would have most likely returned outputs with a mix of sci-fi and family animation films. TaaS paired them with an animated wordless film, a meditative time-spanning drama, and an Irish folk fairy tale since the user's language (music guiding intensity, themes carried through sound, emotion through composition) pointed to a sensibility about music-driven emotional storytelling, rather than just film genre.

## Setup

#### Requirements 
Python 3.10+ and an Anthropic API key ([console.anthropic.com](https://console.anthropic.com)).

#### Clone the repository 
```bash
git clone https://github.com/YOUR_USERNAME/taas-mvp.git
cd taas-mvp
```

#### Set up Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate          # macOS / Linux
venv\Scripts\Activate.ps1         # Windows
pip install -r requirements.txt
```

#### Add API Key 
```bash
cp .env.example .env
```

#### Run The App

Opens at `http://localhost:8501`:
```bash
streamlit run app.py
```

## Project Limitations

- **Shorter inputs produced flatter profiles.** 
When testing different user type prompts for inputs, such as a short one sentence user prompt ("inception is sick. the hallway fight."), the system produces reasonable output, but the taste profile loses specificity in its interpretation. Richer input produces sharper inference, which is both a feature and a limitation.

- **No evaluation for the quality of recommendations.** 
There is no feedback loop to test whether the recommendations match whether the users would watch the films, whether they'd feel the profile was accurate, or whether the film picks hold up over time. Building this would be the next step if I kept iterating for a better version of the app.