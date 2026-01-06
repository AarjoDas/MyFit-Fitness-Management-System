import React, { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'member' | 'trainer' | 'admin' | null;

interface AuthContextType {
  userRole: UserRole;
  userId: number | null;
  setUser: (role: UserRole, id: number) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [userId, setUserId] = useState<number | null>(null);

  const setUser = (role: UserRole, id: number) => {
    setUserRole(role);
    setUserId(id);
  };

  const logout = () => {
    setUserRole(null);
    setUserId(null);
  };

  return (
    <AuthContext.Provider value={{ userRole, userId, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

