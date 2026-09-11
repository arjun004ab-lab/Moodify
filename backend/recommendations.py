MUSIC_DATABASE={m:[{"title":f"Moodify {m.title()} Flow","artist":"Moodify Original Demo","genre":"Original Instrumental","mood":m,"src":f"/music/{m}-01.mp3"}] for m in ["happy","sad","angry","fear","disgust","surprise","neutral"]}
ALIASES={"joy":"happy","happiness":"happy","anger":"angry","fearful":"fear","scared":"fear","disgusted":"disgust","surprised":"surprise","sadness":"sad","calm":"neutral"}
def normalize_emotion(value):
    v=str(value or "neutral").strip().lower()
    return v if v in MUSIC_DATABASE else ALIASES.get(v,"neutral")
def get_recommendation(emotion):
    m=normalize_emotion(emotion)
    return {"emotion":m,"music":MUSIC_DATABASE[m]}
