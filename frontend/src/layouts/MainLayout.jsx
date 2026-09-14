import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <div className="app-layout">

      <Header />

      <div className="app-body">

        <Sidebar />

        <main className="main-content">
          <Outlet />
        </main>

      </div>

    </div>
  );
};

export default MainLayout;