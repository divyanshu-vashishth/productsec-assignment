export interface User {
    username: string;
    email: string | null;
    full_name: string | null;
  }
  
  export interface Project {
    id: number;
    name: string;
    owner: string;
  }
  
  export interface AuthProps {
    setIsAuthenticated: (value: boolean) => void;
  }