import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AuthProps, User, Project } from '../types/auth';

const Dashboard: React.FC<AuthProps> = ({ setIsAuthenticated }) => {
  const [userData, setUserData] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const config = {
          headers: { Authorization: `Bearer ${token}` }
        };

        const [userResponse, projectsResponse] = await Promise.all([
          axios.get<User>('http://localhost:8000/users/me', config),
          axios.get<Project[]>('http://localhost:8000/projects', config)
        ]);

        setUserData(userResponse.data);
        setProjects(projectsResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        handleLogout();
      }
    };

    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow mb-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Dashboard</h1>
            </div>
            <div className="flex items-center">
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {userData && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>User Information</CardTitle>
            </CardHeader>
            <CardContent>
              <p>Username: {userData.username}</p>
              <p>Full Name: {userData.full_name}</p>
              <p>Email: {userData.email}</p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Your Projects</CardTitle>
          </CardHeader>
          <CardContent>
            {projects.length > 0 ? (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {projects.map((project) => (
                  <Card key={project.id}>
                    <CardContent className="p-4">
                      <h3 className="font-medium">{project.name}</h3>
                      <p className="text-gray-500">ID: {project.id}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <p>No projects found.</p>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;