import './App.css';
// import Dashboard from './Dashboard';
import { BrowserRouter } from "react-router-dom";
import AppRouter from './AppRouter';


function App() {
  return (
    <div className="App">
      {/* <Dashboard></Dashboard> */}
      <BrowserRouter>
          <AppRouter></AppRouter>
      </BrowserRouter>
      
    </div>
  );
}

export default App;
