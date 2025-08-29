import React, { useRef, useEffect, useCallback } from 'react';
import { Box, Typography, Card, CardContent, Chip, IconButton } from '@mui/material';
import { Refresh, Psychology, Timeline } from '@mui/icons-material';

const PatternCanvas = ({ width = 400, height = 300, crypto, pattern }) => {
  const canvasRef = useRef(null);

  // Generate realistic crypto price data with pattern
  const generatePriceData = (symbol, patternType) => {
    const basePrice = {
      'BTCUSDT': 108714,
      'ETHUSDT': 4334,
      'SOLUSDT': 214
    }[symbol] || 50000;

    const points = [];
    const numPoints = 50;

    // Generate base trend
    for (let i = 0; i < numPoints; i++) {
      const x = i;
      let y = basePrice;

      // Add pattern-specific shapes
      switch (patternType) {
        case 'head_and_shoulders':
          // Create head and shoulders pattern
          if (i < 15) {
            y += Math.sin(i * 0.4) * basePrice * 0.1; // Left shoulder
          } else if (i < 35) {
            y += Math.sin((i - 15) * 0.3) * basePrice * 0.15; // Head
          } else {
            y += Math.sin((i - 35) * 0.4) * basePrice * 0.08; // Right shoulder
          }
          break;

        case 'cup_and_handle':
          // Create cup and handle pattern
          if (i < 30) {
            y -= Math.pow((i - 15) / 15, 2) * basePrice * 0.1; // Cup
          } else if (i < 45) {
            y -= basePrice * 0.02; // Handle
          } else {
            y += (i - 45) * basePrice * 0.01; // Breakout
          }
          break;

        case 'ascending_triangle':
          // Create ascending triangle
          const resistance = basePrice * 1.05;
          const supportTrend = basePrice * (1 + (i / numPoints) * 0.03);
          y = supportTrend + Math.sin(i * 0.3) * (resistance - supportTrend) * 0.5;
          break;

        case 'double_bottom':
          // Create double bottom pattern
          if (i < 20) {
            y -= Math.sin(i * 0.3) * basePrice * 0.08; // First bottom
          } else if (i < 30) {
            y += (i - 20) * basePrice * 0.005; // Recovery
          } else if (i < 40) {
            y -= Math.sin((i - 30) * 0.3) * basePrice * 0.08; // Second bottom
          } else {
            y += (i - 40) * basePrice * 0.01; // Breakout
          }
          break;

        case 'bullish_flag':
          // Create bullish flag
          if (i < 20) {
            y += i * basePrice * 0.01; // Flagpole up
          } else if (i < 40) {
            y = basePrice * 1.2 - (i - 20) * basePrice * 0.005; // Flag decline
          } else {
            y += (i - 40) * basePrice * 0.015; // Breakout
          }
          break;

        default:
          // Default trend with some volatility
          y += Math.sin(i * 0.2) * basePrice * 0.05 + (Math.random() - 0.5) * basePrice * 0.02;
          break;
      }

      // Add some noise
      y += (Math.random() - 0.5) * basePrice * 0.01;

      points.push({ x: (x / numPoints) * width, y, price: y });
    }

    return points;
  };

  // Draw the chart with pattern overlay
  const drawChart = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const data = generatePriceData(crypto.symbol, pattern.pattern);

    // Clear canvas
    ctx.fillStyle = 'rgba(12, 12, 12, 0.9)';
    ctx.fillRect(0, 0, width, height);

    // Create gradient background
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, 'rgba(0, 212, 255, 0.1)');
    gradient.addColorStop(1, 'rgba(124, 77, 255, 0.1)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    // Calculate price range for scaling
    const prices = data.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    const padding = 40;

    // Scale function
    const scaleY = (price) => height - padding - ((price - minPrice) / priceRange) * (height - 2 * padding);

    // Draw grid lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 1; i < 5; i++) {
      const y = (i / 5) * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Draw price line with gradient
    const lineGradient = ctx.createLinearGradient(0, 0, width, 0);
    lineGradient.addColorStop(0, '#00d4ff');
    lineGradient.addColorStop(0.5, '#7c4dff');
    lineGradient.addColorStop(1, '#00d4ff');

    ctx.strokeStyle = lineGradient;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();
    data.forEach((point, index) => {
      const x = point.x;
      const y = scaleY(point.price);
      
      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    ctx.stroke();

    // Draw pattern recognition overlay
    if (pattern.pattern) {
      drawPatternOverlay(ctx, data, scaleY, pattern);
    }

    // Draw price points with glow effect
    ctx.shadowColor = '#00d4ff';
    ctx.shadowBlur = 10;
    data.forEach((point, index) => {
      if (index % 5 === 0) { // Draw every 5th point
        ctx.fillStyle = '#00d4ff';
        ctx.beginPath();
        ctx.arc(point.x, scaleY(point.price), 3, 0, 2 * Math.PI);
        ctx.fill();
      }
    });
    ctx.shadowBlur = 0;

    // Draw current price indicator
    const currentPoint = data[data.length - 1];
    ctx.fillStyle = pattern.sentiment === 'bullish' ? '#4caf50' : pattern.sentiment === 'bearish' ? '#f44336' : '#ff9800';
    ctx.beginPath();
    ctx.arc(currentPoint.x, scaleY(currentPoint.price), 6, 0, 2 * Math.PI);
    ctx.fill();

    // Draw price labels
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Inter';
    ctx.textAlign = 'right';
    ctx.fillText(`$${maxPrice.toLocaleString()}`, width - 5, padding);
    ctx.fillText(`$${minPrice.toLocaleString()}`, width - 5, height - padding + 15);
  }, [width, height, crypto, pattern]);

  // Draw pattern-specific overlay annotations
  const drawPatternOverlay = (ctx, data, scaleY, pattern) => {
    ctx.save();
    
    const confidence = pattern.confidence || 0.8;
    const alpha = Math.max(0.3, confidence);
    
    switch (pattern.pattern) {
      case 'head_and_shoulders':
        // Draw trend lines for head and shoulders
        ctx.strokeStyle = `rgba(255, 159, 0, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        
        // Neckline
        const necklineY = scaleY(data[10].price);
        ctx.beginPath();
        ctx.moveTo(data[10].x, necklineY);
        ctx.lineTo(data[40].x, necklineY);
        ctx.stroke();
        
        // Labels
        ctx.fillStyle = `rgba(255, 159, 0, ${alpha})`;
        ctx.font = '10px Inter';
        ctx.fillText('Head', data[25].x - 10, scaleY(data[25].price) - 10);
        break;

      case 'ascending_triangle':
        // Draw resistance and support lines
        ctx.strokeStyle = `rgba(76, 175, 80, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.setLineDash([3, 3]);
        
        // Resistance line (horizontal)
        const resistanceY = scaleY(Math.max(...data.map(d => d.price)) * 0.98);
        ctx.beginPath();
        ctx.moveTo(0, resistanceY);
        ctx.lineTo(width, resistanceY);
        ctx.stroke();
        
        // Support line (ascending)
        ctx.beginPath();
        ctx.moveTo(0, scaleY(data[0].price));
        ctx.lineTo(width, resistanceY);
        ctx.stroke();
        break;

      case 'cup_and_handle':
        // Draw cup outline
        ctx.strokeStyle = `rgba(124, 77, 255, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);
        
        // Cup arc
        const centerX = width * 0.4;
        const centerY = scaleY(data[15].price);
        ctx.beginPath();
        ctx.arc(centerX, centerY, width * 0.2, 0, Math.PI, false);
        ctx.stroke();
        break;

      default:
        // No pattern overlay
        break;
    }
    
    ctx.restore();
  };

  // Animation loop
  useEffect(() => {
    const animate = () => {
      drawChart();
      setTimeout(() => {
        requestAnimationFrame(animate);
      }, 2000); // Update every 2 seconds
    };

    animate();
  }, [drawChart]);

  const getPatternDescription = (patternType) => {
    const descriptions = {
      'head_and_shoulders': 'Reversal pattern indicating potential downtrend',
      'cup_and_handle': 'Bullish continuation pattern with breakout potential',
      'ascending_triangle': 'Bullish pattern with rising support and horizontal resistance',
      'double_bottom': 'Reversal pattern suggesting upward price movement',
      'bullish_flag': 'Short-term consolidation in an uptrend',
      'bearish_flag': 'Short-term consolidation in a downtrend',
      'double_top': 'Reversal pattern indicating potential downtrend',
      'descending_triangle': 'Bearish pattern with falling resistance'
    };
    return descriptions[patternType] || 'Technical analysis pattern detected';
  };

  const getPatternEmoji = (patternType) => {
    const emojis = {
      'head_and_shoulders': '👤',
      'cup_and_handle': '☕',
      'ascending_triangle': '📈',
      'double_bottom': '⚖️',
      'bullish_flag': '🚩',
      'bearish_flag': '🔻',
      'double_top': '🔝',
      'descending_triangle': '📉'
    };
    return emojis[patternType] || '📊';
  };

  return (
    <Card sx={{ width: '100%', maxWidth: 500 }}>
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight="bold">
            {getPatternEmoji(pattern.pattern)} Pattern Analysis
          </Typography>
          <IconButton size="small" onClick={() => drawChart()}>
            <Refresh />
          </IconButton>
        </Box>

        {/* Canvas */}
        <Box 
          sx={{ 
            background: 'linear-gradient(135deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 100%)',
            borderRadius: 2,
            p: 1,
            mb: 2
          }}
        >
          <canvas
            ref={canvasRef}
            width={width}
            height={height}
            style={{
              width: '100%',
              height: 'auto',
              borderRadius: '8px',
              cursor: 'crosshair'
            }}
          />
        </Box>

        {/* Pattern Info */}
        <Box>
          <Box display="flex" gap={1} mb={1}>
            <Chip
              icon={<Psychology />}
              label={pattern.pattern.replace('_', ' ').toUpperCase()}
              color="primary"
              size="small"
            />
            <Chip
              label={`${(pattern.confidence * 100).toFixed(1)}% confidence`}
              color="success"
              size="small"
            />
            <Chip
              label={pattern.sentiment}
              color={pattern.sentiment === 'bullish' ? 'success' : 'error'}
              size="small"
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {getPatternDescription(pattern.pattern)}
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            <Timeline fontSize="small" color="primary" />
            <Typography variant="body2" color="text.secondary">
              Timeframe: {pattern.timeframe || '4h'} • Risk: {pattern.risk_level || 'medium'}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PatternCanvas;