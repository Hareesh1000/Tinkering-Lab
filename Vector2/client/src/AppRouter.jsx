import React from 'react'
import { Route, Routes } from 'react-router-dom';


import Dashboard from './Dashboard';
import AppMain from './AppMain';
import Clients from './Clients'

function AppRouter() {
  return (
    <div>
        <Routes>
            <Route path='/' element={<AppMain></AppMain>}></Route>
            <Route path='/clients' element={<Clients></Clients>}></Route>
        </Routes>
    </div>
  )
}

export default AppRouter