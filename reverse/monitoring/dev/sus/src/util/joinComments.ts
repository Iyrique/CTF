export const joinComments = (node: any) => (node.comments as any[] ?? []).map(i => i.value).join('\n')