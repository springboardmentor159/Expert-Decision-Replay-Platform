import React from 'react';
import { useAuth } from '../../context/AuthContext';
import { EmployeeDashboard } from './EmployeeDashboard';
import { ReviewerDashboard } from './ReviewerDashboard';
import { ManagerDashboard } from './ManagerDashboard';
import { AdminDashboard } from './AdminDashboard';

export const DashboardPage = ({ onNavigate }) => {
  const { role } = useAuth();

  switch (role) {
    case 'Administrator':
      return <AdminDashboard onNavigate={onNavigate} />;
    case 'Manager':
      return <ManagerDashboard onNavigate={onNavigate} />;
    case 'Reviewer':
      return <ReviewerDashboard onNavigate={onNavigate} />;
    case 'Employee':
    default:
      return <EmployeeDashboard onNavigate={onNavigate} />;
  }
};
