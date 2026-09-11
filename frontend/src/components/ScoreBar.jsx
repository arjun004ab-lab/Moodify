import React from "react";
export default function ScoreBar({label,value}){const n=Math.max(0,Math.min(100,Number(value)||0));return <div className="score-row"><div className="score-top"><span>{label}</span><strong>{n.toFixed(1)}%</strong></div><div className="score-track"><span className="score-fill" style={{width:`${n}%`}}/></div></div>;}
