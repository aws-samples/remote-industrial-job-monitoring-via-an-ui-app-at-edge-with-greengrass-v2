import "./App.css";
import { Routes, Route } from "react-router-dom";
import FileUpload from "./pages/upload/FileUpload";
import Job from "./pages/job/Job";

function App() {
  localStorage.setItem("IpAddress", "52.27.146.26".replace(/\s+/g, ""));

  return (
    <Routes>
      <Route path="/" element={<FileUpload />} />
      <Route path="fileUpload" element={<FileUpload />} />
      <Route path="job" element={<Job />} />
    </Routes>
  );
}

export default App;
