import { Routes, Route } from "react-router";
import Login from "./pages/Authentication/Login/Login";
import { Container, useMantineColorScheme } from "@mantine/core";
import '@mantine/core/styles.css';
import Signup from "./pages/Authentication/Signup/Signup";
import UserDashboard from "./pages/User/UserDashboard/UserDashboard";

const App = () => {
  const {setColorScheme} = useMantineColorScheme()
  setColorScheme("dark")
  return (
    <Container w={"100%"} h={"100%"}>
      <Routes>
        <Route path="/" element={<h1>Main Page</h1>} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup/>} />
        <Route path="/main" element={<UserDashboard/>} />
        <Route path="/*" element={<h1>404 Page Not Found</h1>} />
      </Routes>
    </Container>
  );
};

export default App;
