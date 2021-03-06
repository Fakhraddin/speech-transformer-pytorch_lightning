import torch as t
from src.model.transformer_rezero.customized_modules.rezero_multi_head_attention import MultiHeadAttentionReZeroBlock
from src.model.transformer_rezero.customized_modules.rezero_feed_forward import FeedForwardReZeroBlock


class TransformerEncoder(t.nn.Module):
    """
    transformer encoder
    """
    def __init__(self, input_size, feed_forward_size, hidden_size, dropout, num_head, num_layer, use_low_rank=False):
        super(TransformerEncoder, self).__init__()
        self.layers = t.nn.ModuleList(
            [TransformerEncoderLayer(input_size, feed_forward_size, hidden_size, dropout, num_head, use_low_rank) for _ in range(num_layer)]
        )

    def forward(self, net, src_mask, self_attention_mask):
        non_pad_mask = ~src_mask.unsqueeze(-1)
        for layer in self.layers:
            net = layer(net, non_pad_mask, self_attention_mask)
        return net


class TransformerEncoderLayer(t.nn.Module):
    def __init__(self, input_size, feed_forward_size, hidden_size, dropout, num_head, use_low_rank=False):
        super(TransformerEncoderLayer, self).__init__()
        self.multi_head_attention_block = MultiHeadAttentionReZeroBlock(input_size, hidden_size, dropout, num_head, use_low_rank)
        self.feed_foward_block = FeedForwardReZeroBlock(input_size, feed_forward_size, dropout)

    def forward(self, src, src_mask, self_attention_mask=None):

        net = self.multi_head_attention_block(src, src, src, self_attention_mask)
        net.masked_fill_(src_mask, 0.0)
        net = self.feed_foward_block(net)
        net.masked_fill_(src_mask, 0.0)
        return net