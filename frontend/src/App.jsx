import React from "react";
import {BrowserRouter,Routes,Route,Navigate} from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import ScanHub from "./pages/ScanHub";
import EmotionScan from "./pages/EmotionScan";
import BeautyScan from "./pages/BeautyScan";
import ResearchDashboard from "./pages/ResearchDashboard";

function ProtectedRoute({children}){
  return localStorage.getItem("moodify_token") ? children : <Navigate to="/login" replace/>;
}

export default function App(){
  return <BrowserRouter><Routes>
    <Route path="/" element={<Landing/>}/>
    <Route path="/login" element={<Login/>}/>
    <Route path="/register" element={<Register/>}/>
    <Route path="/dashboard" element={<ProtectedRoute><Dashboard/></ProtectedRoute>}/>
    <Route path="/scan" element={<ProtectedRoute><ScanHub/></ProtectedRoute>}/>
    <Route path="/camera" element={<Navigate to="/scan/emotion" replace/>}/>
    <Route path="/scan/emotion" element={<ProtectedRoute><EmotionScan/></ProtectedRoute>}/>
    <Route path="/scan/beauty" element={<ProtectedRoute><BeautyScan/></ProtectedRoute>}/>
    <Route path="/research" element={<ProtectedRoute><ResearchDashboard/></ProtectedRoute>}/>
    <Route path="*" element={<Navigate to="/" replace/>}/>
  </Routes></BrowserRouter>;
}
