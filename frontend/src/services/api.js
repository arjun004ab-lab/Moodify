const API_BASE=import.meta.env.VITE_API_URL||"http://127.0.0.1:8000";

async function request(path,options={}){
  const headers=new Headers(options.headers||{});
  const token=localStorage.getItem("moodify_token");
  if(token) headers.set("Authorization",`Bearer ${token}`);
  const response=await fetch(`${API_BASE}${path}`,{...options,headers});
  const raw=await response.text();
  let data={};
  try{data=raw?JSON.parse(raw):{}}catch{data={detail:raw||"Unexpected server response."};}
  if(!response.ok){
    const message=Array.isArray(data.detail)?data.detail.map(x=>x.msg).join(", "):data.detail||`Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}
export const api={
  get:path=>request(path),
  postJson:(path,body)=>request(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}),
  postFile:(path,file)=>{const form=new FormData();form.append("file",file);return request(path,{method:"POST",body:form});}
};
export {API_BASE};
