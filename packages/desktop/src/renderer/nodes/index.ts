import { SourceNode } from './SourceNode';
import { TransformNode } from './TransformNode';
import { ActionNode } from './ActionNode';
import { GuardNode } from './GuardNode';

export const nodeTypes = {
  midioSource: SourceNode,
  midioTransform: TransformNode,
  midioAction: ActionNode,
  midioGuard: GuardNode,
};
