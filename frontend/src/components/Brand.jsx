import React from "react";
import {Link} from "react-router-dom";
export default function Brand({large=false}){return <Link to="/" className={`brand ${large?"brand-large":""}`}><span className="brand-mark">M</span><span>Moodify</span></Link>;}
