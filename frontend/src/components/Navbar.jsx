import React from "react";
import {Activity,BarChart3,LogOut,ScanFace} from "lucide-react";
import {Link,useLocation,useNavigate} from "react-router-dom";
import Brand from "./Brand";
export default function Navbar(){
 const location=useLocation(),navigate=useNavigate();
 const user=JSON.parse(localStorage.getItem("moodify_user")||"null");
 const logout=()=>{localStorage.removeItem("moodify_token");localStorage.removeItem("moodify_user");navigate("/login",{replace:true});};
 return <header className="navbar"><Brand/><nav className="nav-links"><Link to="/dashboard" className={location.pathname==="/dashboard"?"active":""}><Activity size={15}/>Overview</Link><Link to="/scan" className={location.pathname.startsWith("/scan")?"active":""}><ScanFace size={15}/>Scan Studio</Link><Link to="/research" className={location.pathname.startsWith("/research")?"active":""}><BarChart3 size={15}/>Research</Link></nav><div className="nav-right"><span className="ai-status"><span className="pulse-dot"/>AI ONLINE</span><div className="avatar">{(user?.name||"U").charAt(0).toUpperCase()}</div><button type="button" className="icon-button" onClick={logout} aria-label="Sign out"><LogOut size={16}/></button></div></header>;
}
