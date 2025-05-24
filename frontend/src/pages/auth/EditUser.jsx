import React from 'react';
import UserForm from './UserForm';

const EditUser = ({ isAdmin }) => {
  return <UserForm isAdmin={isAdmin} isEdit={true} />;
};

export default EditUser; 