import React from "react";
export default function MetricCard({number,label,detail}){return <article className="metric-card glass"><strong>{number}</strong><span>{label}</span><small>{detail}</small></article>;}
