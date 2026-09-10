import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { EmployeeDashboard } from './EmployeeDashboard';
import { ReviewerDashboard } from './ReviewerDashboard';
import { ManagerDashboard } from './ManagerDashboard';
import { AdminDashboard } from './AdminDashboard';

export const DashboardRouter = () => {
  const { user } = useAuth();

  switch (user?.role) {
    case 'Administrator':
      return <AdminDashboard />;
    case 'Manager':
      return <ManagerDashboard />;
    case 'Reviewer':
      return <ReviewerDashboard />;
    case 'Employee':
    default:
      return <EmployeeDashboard />;
  }
};
