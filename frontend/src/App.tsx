import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { MantineProvider, createTheme, AppShell, Group, Title, Container, Button, ActionIcon, useMantineColorScheme, ColorSchemeScript } from '@mantine/core';
import { useEffect, useState } from 'react';
import { Home } from './pages/Home';
import { Editor } from './pages/Editor';
import { View } from './pages/View';
import { NavLink } from 'react-router-dom';
import { IconBook2, IconBrandGithub, IconSun, IconMoon } from '@tabler/icons-react';
import '@mantine/core/styles.css';
import './App.css';

// Create a custom theme
const theme = createTheme({
  primaryColor: 'indigo',
  primaryShade: 6,
  fontFamily: 'Poppins, sans-serif',
  headings: {
    fontFamily: 'Poppins, sans-serif',
    fontWeight: '600',
  },
  colors: {
    indigo: [
      '#edf2ff', // 0
      '#dbe4ff', // 1
      '#bac8ff', // 2
      '#91a7ff', // 3
      '#748ffc', // 4
      '#5c7cfa', // 5
      '#4c6ef5', // 6 - primary
      '#4263eb', // 7
      '#3b5bdb', // 8
      '#364fc7', // 9
    ],
  },
  components: {
    Button: {
      defaultProps: {
        radius: 'md',
      },
    },
  },
});

// Define indigo color for use in components
const indigoColor = '#4c6ef5';

// Dark mode toggle component
function DarkModeToggle() {
  const { colorScheme, setColorScheme } = useMantineColorScheme();
  const isDark = colorScheme === 'dark';

  const toggleColorScheme = () => {
    const newColorScheme = isDark ? 'light' : 'dark';
    setColorScheme(newColorScheme);
    
    // Update HTML class for global CSS selectors
    document.documentElement.classList.toggle('dark', newColorScheme === 'dark');
    
    // Save preference to localStorage
    localStorage.setItem('color-scheme', newColorScheme);
  };

  return (
    <ActionIcon
      variant="outline"
      color={isDark ? 'yellow' : 'indigo'}
      onClick={toggleColorScheme}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="transition-all duration-200"
    >
      {isDark ? <IconSun size={18} /> : <IconMoon size={18} />}
    </ActionIcon>
  );
}

function App() {
  const [colorScheme, setColorScheme] = useState<'light' | 'dark' | 'auto'>('auto');
  
  // Initialize color scheme from localStorage or system preference
  useEffect(() => {
    const savedColorScheme = localStorage.getItem('color-scheme') as 'light' | 'dark' | null;
    
    if (savedColorScheme) {
      setColorScheme(savedColorScheme);
      document.documentElement.classList.toggle('dark', savedColorScheme === 'dark');
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', prefersDark);
      setColorScheme(prefersDark ? 'dark' : 'light');
    }
  }, []);
  
  // Listen for system preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      // Only update if user hasn't set a preference
      if (!localStorage.getItem('color-scheme')) {
        document.documentElement.classList.toggle('dark', e.matches);
        setColorScheme(e.matches ? 'dark' : 'light');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return (
    <>
      <ColorSchemeScript defaultColorScheme={colorScheme} />
      <MantineProvider theme={theme} defaultColorScheme={colorScheme}>
        <Router>
          <AppShell
            header={{ height: 60 }}
            padding="md"
            className="transition-colors duration-300"
          >
            <AppShell.Header>
              <Container size="lg" h="100%">
                <Group justify="space-between" h="100%">
                  <Group>
                    <IconBook2 size={28} stroke={1.5} color={indigoColor} />
                    <NavLink to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
                      <Title order={2} c="indigo.6">MangaLens</Title>
                    </NavLink>
                  </Group>
                  <Group>
                    <DarkModeToggle />
                    <Button 
                      component="a" 
                      href="https://github.com/antijun/MangaLens" 
                      target="_blank"
                      variant="subtle"
                      leftSection={<IconBrandGithub size={18} />}
                    >
                      GitHub
                    </Button>
                  </Group>
                </Group>
              </Container>
            </AppShell.Header>

            <AppShell.Main>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/editor/:imageId" element={<Editor />} />
                <Route path="/view/:imageId" element={<View />} />
              </Routes>
            </AppShell.Main>
          </AppShell>
        </Router>
      </MantineProvider>
    </>
  );
}

export default App;
