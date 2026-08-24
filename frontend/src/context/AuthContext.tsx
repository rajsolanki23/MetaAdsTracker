import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchApi } from '../api/client';
import { LoginResponse } from '../types';

interface AuthUser {
  sub: string;
  email: string;
  role: string;
  name: string;
}

interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const savedUser = localStorage.getItem('cl_auth_user');
    if (savedUser) {
      try {
        return JSON.parse(savedUser);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('cl_auth_token');
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);

    // Verify token validity on boot if token exists
    if (token) {
      fetchApi<{ authenticated: boolean; user: AuthUser }>('/auth/me')
        .then((res) => {
          if (res.user) {
            setUser({
              sub: res.user.email || res.user.sub,
              email: res.user.email || res.user.sub,
              role: res.user.role || 'admin',
              name: res.user.name || 'Operator',
            });
            localStorage.setItem('cl_auth_user', JSON.stringify(res.user));
          }
        })
        .catch(() => {
          logout();
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }

    return () => {
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, []);

  const login = async (email: string, password: string) => {
    const res = await fetchApi<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    const authUser: AuthUser = {
      sub: res.user.sub,
      email: res.user.sub,
      role: res.user.role,
      name: res.user.name,
    };

    setToken(res.access_token);
    setUser(authUser);

    localStorage.setItem('cl_auth_token', res.access_token);
    localStorage.setItem('cl_auth_user', JSON.stringify(authUser));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('cl_auth_token');
    localStorage.removeItem('cl_auth_user');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: Boolean(token && user),
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
