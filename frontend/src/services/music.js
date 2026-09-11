const MUSIC_LIBRARY = {
  happy: [
    {
      title: "Moodify Happy Flow",
      artist: "Moodify Original",
      genre: "Electronic / Uplifting",
      src: "/music/happy-01.mp3"
    }
  ],

  sad: [
    {
      title: "Moodify Sad Flow",
      artist: "Moodify Original",
      genre: "Ambient / Reflective",
      src: "/music/sad-01.mp3"
    }
  ],

  angry: [
    {
      title: "Moodify Angry Flow",
      artist: "Moodify Original",
      genre: "Pulse / Energy",
      src: "/music/angry-01.mp3"
    }
  ],

  fear: [
    {
      title: "Moodify Fear Flow",
      artist: "Moodify Original",
      genre: "Dark Ambient",
      src: "/music/fear-01.mp3"
    }
  ],

  surprise: [
    {
      title: "Moodify Surprise Flow",
      artist: "Moodify Original",
      genre: "Cinematic / Bright",
      src: "/music/surprise-01.mp3"
    }
  ],

  disgust: [
    {
      title: "Moodify Reset Flow",
      artist: "Moodify Original",
      genre: "Minimal / Pulse",
      src: "/music/disgust-01.mp3"
    }
  ],

  neutral: [
    {
      title: "Moodify Neutral Flow",
      artist: "Moodify Original",
      genre: "Focus / Ambient",
      src: "/music/neutral-01.mp3"
    }
  ]
};

const EMOTION_ALIASES = {
  joy: "happy",
  happiness: "happy",
  anger: "angry",
  fearful: "fear",
  scared: "fear",
  disgusted: "disgust",
  surprised: "surprise",
  sadness: "sad",
  calm: "neutral"
};

function normalizeMood(emotion) {
  const value = String(emotion || "neutral")
    .trim()
    .toLowerCase();

  if (
    Object.prototype.hasOwnProperty.call(
      MUSIC_LIBRARY,
      value
    )
  ) {
    return value;
  }

  return EMOTION_ALIASES[value] || "neutral";
}

function getMusicForMood(emotion) {
  const mood = normalizeMood(emotion);

  return (
    MUSIC_LIBRARY[mood] ||
    MUSIC_LIBRARY.neutral
  );
}

export {
  MUSIC_LIBRARY,
  EMOTION_ALIASES,
  normalizeMood,
  getMusicForMood
};

export default MUSIC_LIBRARY;
