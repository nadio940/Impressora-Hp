import React from 'react';
import { Card, CardContent, Typography, Box, SvgIconProps } from '@mui/material';

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ReactElement<SvgIconProps>;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  subtitle?: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, subtitle }) => {
  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="h2">
              {value}
            </Typography>
            {subtitle && (
              <Typography color="textSecondary" variant="body2">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 56,
              height: 56,
              borderRadius: '50%',
              backgroundColor: (theme) => theme.palette[color].main,
              color: 'white',
            }}
          >
            {React.cloneElement(icon, { fontSize: 'large' })}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default StatCard;
