# Task 03: Thinking Boxes Visualization

**Goal:** React components that replicate terminal Rich Layout thinking boxes

## Context

The signature UX of Agent Cube is the thinking boxes. This task brings them to the web.

## Requirements

### 1. ThinkingBox Component

```tsx
<ThinkingBox
  title="Writer A"
  icon="💭"
  color="green"
  thoughts={["Analyzing requirements...", "Creating structure...", "Writing tests..."]}
  maxLines={3}
/>
```

**Features:**
- Last N thoughts visible (configurable)
- Auto-scroll (new thoughts push old ones out)
- Matching terminal colors
- Smooth transitions

### 2. Layout Variants

**DualThinking:**
```tsx
<DualThinking
  agentA={{title: "Writer A", thoughts: [...]}}
  agentB={{title: "Writer B", thoughts: [...]}}
/>
```

**TripleThinking:**
```tsx
<TripleThinking
  judges={[
    {title: "Judge 1", thoughts: [...]},
    {title: "Judge 2", thoughts: [...]},
    {title: "Judge 3", thoughts: [...]}
  ]}
/>
```

### 3. Stream Integration

```tsx
const { thinking } = useWorkflowStream(taskId)

<DualThinking
  agentA={{...thinking.writerA}}
  agentB={{...thinking.writerB}}
/>
```

Updates in real-time as events arrive!

### 4. Styling

Match terminal aesthetics:
- Dimmed borders
- Monospace font for code snippets
- Green for Writer A / Judge 1
- Blue for Writer B / Judge 2
- Purple for Judge 3 / Gemini

## Deliverables

- [ ] `<ThinkingBox>` component
- [ ] `<DualThinking>` layout
- [ ] `<TripleThinking>` layout
- [ ] Real-time updates from SSE stream
- [ ] Auto-scroll old thoughts out
- [ ] Matches terminal visual style
- [ ] Smooth animations
- [ ] Works with live stream data

## Architecture Constraints

**Component Design:**
- ✅ Controlled components (thoughts passed as props)
- ✅ Pure presentation (no business logic)
- ✅ TypeScript interfaces for props
- ❌ No local state for thoughts (comes from stream)
- ❌ No direct API calls (use hooks)

**Performance:**
- ✅ Virtualization for long thought lists
- ✅ Memoization for expensive renders
- ✅ Debounced updates (max 10/sec)

**Accessibility:**
- ✅ Proper semantic HTML
- ✅ ARIA labels for boxes
- ✅ Keyboard navigation

## Example Implementation

```tsx
interface ThinkingBoxProps {
  title: string
  thoughts: string[]
  maxLines?: number
  color?: 'green' | 'blue' | 'purple'
}

export function ThinkingBox({ 
  title, 
  thoughts, 
  maxLines = 3,
  color = 'green' 
}: ThinkingBoxProps) {
  const visible = thoughts.slice(-maxLines)
  const colorClasses = {
    green: 'border-green-500/20 text-green-700',
    blue: 'border-blue-500/20 text-blue-700',
    purple: 'border-purple-500/20 text-purple-700'
  }
  
  return (
    <div className={`border ${colorClasses[color]} rounded p-3 font-mono text-sm`}>
      <div className="text-xs opacity-50 mb-2">💭 {title}</div>
      <div className="space-y-1">
        {visible.map((thought, i) => (
          <div key={i} className="opacity-70">{thought}</div>
        ))}
      </div>
    </div>
  )
}
```

## Acceptance Criteria

1. Thinking box shows last N thoughts
2. New thoughts push old ones out
3. Updates smoothly (no flicker)
4. Colors match terminal
5. Works with dual/triple layouts
6. Integrates with SSE stream
7. Looks professional

## Time Estimate

2-3 hours

