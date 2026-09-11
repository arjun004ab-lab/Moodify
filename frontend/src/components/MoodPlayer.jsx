import React,{useCallback,useEffect,useRef,useState} from "react";
import {Pause,Play,SkipForward,Volume2,VolumeX} from "lucide-react";

export default function MoodPlayer({emotion,tracks=[],autoPlay=false,audioContextRef}){
 const sourceRef=useRef(null);const gainRef=useRef(null);const buffersRef=useRef({});
 const[index,setIndex]=useState(0);const[playing,setPlaying]=useState(false);const[muted,setMuted]=useState(false);const[loading,setLoading]=useState(false);
 const track=tracks[index];
 const getContext=useCallback(()=>{
   if(audioContextRef?.current)return audioContextRef.current;
   const Ctx=window.AudioContext||window.webkitAudioContext;if(!Ctx)return null;
   const ctx=new Ctx();if(audioContextRef)audioContextRef.current=ctx;return ctx;
 },[audioContextRef]);
 const loadBuffer=useCallback(async t=>{
   if(!t)return null;if(buffersRef.current[t.src])return buffersRef.current[t.src];
   const ctx=getContext();if(!ctx)return null;const r=await fetch(t.src);if(!r.ok)throw new Error("Music file could not be loaded.");
   const decoded=await ctx.decodeAudioData(await r.arrayBuffer());buffersRef.current[t.src]=decoded;return decoded;
 },[getContext]);
 const stop=useCallback(()=>{if(sourceRef.current){try{sourceRef.current.stop();}catch{}sourceRef.current=null;}setPlaying(false);},[]);
 const play=useCallback(async()=>{if(!track)return;setLoading(true);try{const ctx=getContext();if(!ctx)throw new Error("Web Audio is unavailable.");await ctx.resume();stop();const buffer=await loadBuffer(track);const source=ctx.createBufferSource();const gain=ctx.createGain();source.buffer=buffer;gain.gain.value=muted?0:.82;source.connect(gain);gain.connect(ctx.destination);source.onended=()=>{if(sourceRef.current===source){sourceRef.current=null;setPlaying(false);}};gainRef.current=gain;sourceRef.current=source;source.start();setPlaying(true);}catch(err){console.error("Moodify playback:",err);setPlaying(false);}finally{setLoading(false);}},[getContext,loadBuffer,muted,stop,track]);
 useEffect(()=>{setIndex(0);stop();},[emotion,tracks,stop]);
 useEffect(()=>{if(autoPlay&&track)play();},[autoPlay,track,play]);
 useEffect(()=>()=>stop(),[stop]);
 if(!track)return null;
 const next=()=>{stop();setIndex(i=>(i+1)%tracks.length);};
 const mute=()=>{const m=!muted;setMuted(m);if(gainRef.current)gainRef.current.gain.value=m?0:.82;};
 return <div className="mood-player glass"><div className="player-art"><div className="player-orbit"/><div className="player-core">♪</div></div><div className="player-meta"><div className="eyebrow">ADAPTIVE SOUNDTRACK</div><h3>{track.title}</h3><p>{track.artist}</p><span className="mood-tag">{emotion}</span></div><div className="player-controls"><button type="button" className="player-button main" onClick={()=>playing?stop():play()} disabled={loading}>{loading?"…":playing?<Pause size={18}/>:<Play size={18}/>}</button><button type="button" className="player-button" onClick={next} aria-label="Next track"><SkipForward size={17}/></button><button type="button" className="player-button" onClick={mute} aria-label={muted?"Unmute":"Mute"}>{muted?<VolumeX size={17}/>:<Volume2 size={17}/>}</button></div></div>;
}
