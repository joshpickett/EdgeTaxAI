import { UnifiedDashboard } from '../UnifiedDashboard';
import { useAuth } from '../../hooks/useAuth';

const DashboardScreen = ({ navigation }) => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigation.reset({
      index: 0,
      routes: [{ name: 'Login' }],
    });
  };

  return (
    <UnifiedDashboard userId={user.id} onLogout={handleLogout} />
  );
};

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    padding: spacing.lg, 
    backgroundColor: colors.background.default 
  },
});
