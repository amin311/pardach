import React from 'react';
import UserForm from './UserForm';

const CreateUser = ({ isAdmin }) => {
  return <UserForm isAdmin={isAdmin} isEdit={false} />;
};

export default CreateUser; 