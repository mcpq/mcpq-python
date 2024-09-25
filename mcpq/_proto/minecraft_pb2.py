# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: minecraft.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0fminecraft.proto\x12\x08protocol"\x07\n\x05\x45mpty";\n\x06Status\x12"\n\x04\x63ode\x18\x01 \x01(\x0e\x32\x14.protocol.StatusCode\x12\r\n\x05\x65xtra\x18\x02 \x01(\t"\x17\n\x07Message\x12\x0c\n\x04text\x18\x01 \x01(\t"\'\n\x04Vec3\x12\t\n\x01x\x18\x01 \x01(\x05\x12\t\n\x01y\x18\x02 \x01(\x05\x12\t\n\x01z\x18\x03 \x01(\x05"(\n\x05Vec3f\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\t\n\x01z\x18\x03 \x01(\x02":\n\tBlockInfo\x12\x11\n\tblockType\x18\x01 \x01(\t\x12\x1a\n\x03nbt\x18\x02 \x01(\x0b\x32\r.protocol.NBT"\x13\n\x03NBT\x12\x0c\n\x04snbt\x18\x01 \x01(\t"g\n\x05\x42lock\x12!\n\x04info\x18\x01 \x01(\x0b\x32\x13.protocol.BlockInfo\x12\x1e\n\x05world\x18\x02 \x01(\x0b\x32\x0f.protocol.World\x12\x1b\n\x03pos\x18\x03 \x01(\x0b\x32\x0e.protocol.Vec3"h\n\x06\x42locks\x12!\n\x04info\x18\x01 \x01(\x0b\x32\x13.protocol.BlockInfo\x12\x1e\n\x05world\x18\x02 \x01(\x0b\x32\x0f.protocol.World\x12\x1b\n\x03pos\x18\x03 \x03(\x0b\x32\x0e.protocol.Vec3"8\n\x05World\x12\x0c\n\x04name\x18\x01 \x01(\t\x12!\n\x04info\x18\x02 \x01(\x0b\x32\x13.protocol.WorldInfo"%\n\tWorldInfo\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0b\n\x03pvp\x18\x02 \x01(\x08"/\n\x11\x45ntityOrientation\x12\x0b\n\x03yaw\x18\x01 \x01(\x02\x12\r\n\x05pitch\x18\x02 \x01(\x02"\x80\x01\n\x0e\x45ntityLocation\x12\x1e\n\x05world\x18\x01 \x01(\x0b\x32\x0f.protocol.World\x12\x1c\n\x03pos\x18\x02 \x01(\x0b\x32\x0f.protocol.Vec3f\x12\x30\n\x0borientation\x18\x03 \x01(\x0b\x32\x1b.protocol.EntityOrientation"B\n\x06Player\x12\x0c\n\x04name\x18\x01 \x01(\t\x12*\n\x08location\x18\x02 \x01(\x0b\x32\x18.protocol.EntityLocation"N\n\x06\x45ntity\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04type\x18\x02 \x01(\t\x12*\n\x08location\x18\x03 \x01(\x0b\x32\x18.protocol.EntityLocation"<\n\x12\x45ventStreamRequest\x12&\n\teventType\x18\x01 \x01(\x0e\x32\x13.protocol.EventType"\x93\x05\n\x05\x45vent\x12!\n\x04type\x18\x01 \x01(\x0e\x32\x13.protocol.EventType\x12!\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x10.protocol.StatusH\x00\x12\x35\n\tplayerMsg\x18\x03 \x01(\x0b\x32 .protocol.Event.PlayerAndMessageH\x00\x12,\n\x08\x62lockHit\x18\x04 \x01(\x0b\x32\x18.protocol.Event.BlockHitH\x00\x12\x36\n\rprojectileHit\x18\x05 \x01(\x0b\x32\x1d.protocol.Event.ProjectileHitH\x00\x1a\x46\n\x10PlayerAndMessage\x12!\n\x07trigger\x18\x01 \x01(\x0b\x32\x10.protocol.Player\x12\x0f\n\x07message\x18\x02 \x01(\t\x1a\x7f\n\x08\x42lockHit\x12!\n\x07trigger\x18\x01 \x01(\x0b\x32\x10.protocol.Player\x12\x12\n\nright_hand\x18\x02 \x01(\x08\x12\x11\n\titem_type\x18\x03 \x01(\t\x12\x1b\n\x03pos\x18\x04 \x01(\x0b\x32\x0e.protocol.Vec3\x12\x0c\n\x04\x66\x61\x63\x65\x18\x05 \x01(\t\x1a\xd4\x01\n\rProjectileHit\x12!\n\x07trigger\x18\x01 \x01(\x0b\x32\x10.protocol.Player\x12\x12\n\nprojectile\x18\x02 \x01(\t\x12\x1b\n\x03pos\x18\x03 \x01(\x0b\x32\x0e.protocol.Vec3\x12\x0c\n\x04\x66\x61\x63\x65\x18\x04 \x01(\t\x12"\n\x06player\x18\x05 \x01(\x0b\x32\x10.protocol.PlayerH\x00\x12"\n\x06\x65ntity\x18\x06 \x01(\x0b\x32\x10.protocol.EntityH\x00\x12\x0f\n\x05\x62lock\x18\x07 \x01(\tH\x00\x42\x08\n\x06targetB\x07\n\x05\x65vent"\x13\n\x11ServerInfoRequest"^\n\x12ServerInfoResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12\x11\n\tmcVersion\x18\x02 \x01(\t\x12\x13\n\x0bmcpqVersion\x18\x03 \x01(\t"$\n\x0fMaterialRequest\x12\x11\n\tonly_keys\x18\x01 \x01(\x08"\xd3\x02\n\x10MaterialResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12\x36\n\tmaterials\x18\x02 \x03(\x0b\x32#.protocol.MaterialResponse.Material\x1a\xe4\x01\n\x08Material\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05isAir\x18\x02 \x01(\x08\x12\x0f\n\x07isBlock\x18\x03 \x01(\x08\x12\x12\n\nisBurnable\x18\x04 \x01(\x08\x12\x10\n\x08isEdible\x18\x05 \x01(\x08\x12\x13\n\x0bisFlammable\x18\x06 \x01(\x08\x12\x0e\n\x06isFuel\x18\x07 \x01(\x08\x12\x16\n\x0eisInteractable\x18\x08 \x01(\x08\x12\x0e\n\x06isItem\x18\t \x01(\x08\x12\x13\n\x0bisOccluding\x18\n \x01(\x08\x12\x0f\n\x07isSolid\x18\x0b \x01(\x08\x12\x12\n\nhasGravity\x18\x0c \x01(\x08"&\n\x11\x45ntityTypeRequest\x12\x11\n\tonly_keys\x18\x01 \x01(\x08"\x9e\x01\n\x12\x45ntityTypeResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12\x36\n\x05types\x18\x02 \x03(\x0b\x32\'.protocol.EntityTypeResponse.EntityType\x1a.\n\nEntityType\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x13\n\x0bisSpawnable\x18\x02 \x01(\x08"C\n\x0e\x43ommandRequest\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\t\x12\x10\n\x08\x62locking\x18\x02 \x01(\x08\x12\x0e\n\x06output\x18\x03 \x01(\x08"C\n\x0f\x43ommandResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12\x0e\n\x06output\x18\x02 \x01(\t"D\n\x0f\x43hatPostRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\x12 \n\x06player\x18\x02 \x01(\x0b\x32\x10.protocol.Player"/\n\x0cWorldRequest\x12\x1f\n\x06worlds\x18\x01 \x03(\x0b\x32\x0f.protocol.World"R\n\rWorldResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12\x1f\n\x06worlds\x18\x02 \x03(\x0b\x32\x0f.protocol.World"E\n\rHeightRequest\x12\x1e\n\x05world\x18\x01 \x01(\x0b\x32\x0f.protocol.World\x12\t\n\x01x\x18\x02 \x01(\x05\x12\t\n\x01z\x18\x03 \x01(\x05"R\n\x0eHeightResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12\x1e\n\x05\x62lock\x18\x02 \x01(\x0b\x32\x0f.protocol.Block"]\n\x0c\x42lockRequest\x12\x1b\n\x03pos\x18\x01 \x01(\x0b\x32\x0e.protocol.Vec3\x12\x1e\n\x05world\x18\x02 \x01(\x0b\x32\x0f.protocol.World\x12\x10\n\x08withData\x18\x03 \x01(\x08"T\n\rBlockResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12!\n\x04info\x18\x02 \x01(\x0b\x32\x13.protocol.BlockInfo"5\n\rPlayerRequest\x12\r\n\x05names\x18\x01 \x03(\t\x12\x15\n\rwithLocations\x18\x02 \x01(\x08"U\n\x0ePlayerResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12!\n\x07players\x18\x02 \x03(\x0b\x32\x10.protocol.Player"[\n\x15SpawnedEntityResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12 \n\x06\x65ntity\x18\x02 \x01(\x0b\x32\x10.protocol.Entity"\xc9\x02\n\rEntityRequest\x12<\n\x08specific\x18\x01 \x01(\x0b\x32(.protocol.EntityRequest.SpecificEntitiesH\x00\x12:\n\tworldwide\x18\x02 \x01(\x0b\x32%.protocol.EntityRequest.WorldEntitiesH\x00\x12\x15\n\rwithLocations\x18\x03 \x01(\x08\x1a\x36\n\x10SpecificEntities\x12"\n\x08\x65ntities\x18\x01 \x03(\x0b\x32\x10.protocol.Entity\x1aZ\n\rWorldEntities\x12\x1e\n\x05world\x18\x01 \x01(\x0b\x32\x0f.protocol.World\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x1b\n\x13includeNotSpawnable\x18\x03 \x01(\x08\x42\x13\n\x11\x45ntityRequestType"V\n\x0e\x45ntityResponse\x12 \n\x06status\x18\x01 \x01(\x0b\x32\x10.protocol.Status\x12"\n\x08\x65ntities\x18\x02 \x03(\x0b\x32\x10.protocol.Entity*\xf8\x01\n\nStatusCode\x12\x06\n\x02OK\x10\x00\x12\x11\n\rUNKNOWN_ERROR\x10\x01\x12\x14\n\x10MISSING_ARGUMENT\x10\x02\x12\x14\n\x10INVALID_ARGUMENT\x10\x03\x12\x13\n\x0fNOT_IMPLEMENTED\x10\x04\x12\x13\n\x0fWORLD_NOT_FOUND\x10\x05\x12\x14\n\x10PLAYER_NOT_FOUND\x10\x06\x12\x18\n\x14\x42LOCK_TYPE_NOT_FOUND\x10\x07\x12\x19\n\x15\x45NTITY_TYPE_NOT_FOUND\x10\x08\x12\x18\n\x14\x45NTITY_NOT_SPAWNABLE\x10\t\x12\x14\n\x10\x45NTITY_NOT_FOUND\x10\n*\xa9\x01\n\tEventType\x12\x0e\n\nEVENT_NONE\x10\x00\x12\x15\n\x11\x45VENT_PLAYER_JOIN\x10\x01\x12\x16\n\x12\x45VENT_PLAYER_LEAVE\x10\x02\x12\x16\n\x12\x45VENT_PLAYER_DEATH\x10\x03\x12\x16\n\x12\x45VENT_CHAT_MESSAGE\x10\x04\x12\x13\n\x0f\x45VENT_BLOCK_HIT\x10\x05\x12\x18\n\x14\x45VENT_PROJECTILE_HIT\x10\x06\x32\xea\x08\n\tMinecraft\x12J\n\rgetServerInfo\x12\x1b.protocol.ServerInfoRequest\x1a\x1c.protocol.ServerInfoResponse\x12\x45\n\x0cgetMaterials\x12\x19.protocol.MaterialRequest\x1a\x1a.protocol.MaterialResponse\x12K\n\x0egetEntityTypes\x12\x1b.protocol.EntityTypeRequest\x1a\x1c.protocol.EntityTypeResponse\x12\x38\n\nrunCommand\x12\x18.protocol.CommandRequest\x1a\x10.protocol.Status\x12L\n\x15runCommandWithOptions\x12\x18.protocol.CommandRequest\x1a\x19.protocol.CommandResponse\x12\x39\n\npostToChat\x12\x19.protocol.ChatPostRequest\x1a\x10.protocol.Status\x12?\n\x0c\x61\x63\x63\x65ssWorlds\x12\x16.protocol.WorldRequest\x1a\x17.protocol.WorldResponse\x12>\n\tgetHeight\x12\x17.protocol.HeightRequest\x1a\x18.protocol.HeightResponse\x12;\n\x08getBlock\x12\x16.protocol.BlockRequest\x1a\x17.protocol.BlockResponse\x12-\n\x08setBlock\x12\x0f.protocol.Block\x1a\x10.protocol.Status\x12/\n\tsetBlocks\x12\x10.protocol.Blocks\x1a\x10.protocol.Status\x12\x32\n\x0csetBlockCube\x12\x10.protocol.Blocks\x1a\x10.protocol.Status\x12?\n\ngetPlayers\x12\x17.protocol.PlayerRequest\x1a\x18.protocol.PlayerResponse\x12/\n\tsetPlayer\x12\x10.protocol.Player\x1a\x10.protocol.Status\x12@\n\x0bspawnEntity\x12\x10.protocol.Entity\x1a\x1f.protocol.SpawnedEntityResponse\x12/\n\tsetEntity\x12\x10.protocol.Entity\x1a\x10.protocol.Status\x12@\n\x0bgetEntities\x12\x17.protocol.EntityRequest\x1a\x18.protocol.EntityResponse\x12\x41\n\x0egetEventStream\x12\x1c.protocol.EventStreamRequest\x1a\x0f.protocol.Event0\x01\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "minecraft_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_STATUSCODE"]._serialized_start = 3679
    _globals["_STATUSCODE"]._serialized_end = 3927
    _globals["_EVENTTYPE"]._serialized_start = 3930
    _globals["_EVENTTYPE"]._serialized_end = 4099
    _globals["_EMPTY"]._serialized_start = 29
    _globals["_EMPTY"]._serialized_end = 36
    _globals["_STATUS"]._serialized_start = 38
    _globals["_STATUS"]._serialized_end = 97
    _globals["_MESSAGE"]._serialized_start = 99
    _globals["_MESSAGE"]._serialized_end = 122
    _globals["_VEC3"]._serialized_start = 124
    _globals["_VEC3"]._serialized_end = 163
    _globals["_VEC3F"]._serialized_start = 165
    _globals["_VEC3F"]._serialized_end = 205
    _globals["_BLOCKINFO"]._serialized_start = 207
    _globals["_BLOCKINFO"]._serialized_end = 265
    _globals["_NBT"]._serialized_start = 267
    _globals["_NBT"]._serialized_end = 286
    _globals["_BLOCK"]._serialized_start = 288
    _globals["_BLOCK"]._serialized_end = 391
    _globals["_BLOCKS"]._serialized_start = 393
    _globals["_BLOCKS"]._serialized_end = 497
    _globals["_WORLD"]._serialized_start = 499
    _globals["_WORLD"]._serialized_end = 555
    _globals["_WORLDINFO"]._serialized_start = 557
    _globals["_WORLDINFO"]._serialized_end = 594
    _globals["_ENTITYORIENTATION"]._serialized_start = 596
    _globals["_ENTITYORIENTATION"]._serialized_end = 643
    _globals["_ENTITYLOCATION"]._serialized_start = 646
    _globals["_ENTITYLOCATION"]._serialized_end = 774
    _globals["_PLAYER"]._serialized_start = 776
    _globals["_PLAYER"]._serialized_end = 842
    _globals["_ENTITY"]._serialized_start = 844
    _globals["_ENTITY"]._serialized_end = 922
    _globals["_EVENTSTREAMREQUEST"]._serialized_start = 924
    _globals["_EVENTSTREAMREQUEST"]._serialized_end = 984
    _globals["_EVENT"]._serialized_start = 987
    _globals["_EVENT"]._serialized_end = 1646
    _globals["_EVENT_PLAYERANDMESSAGE"]._serialized_start = 1223
    _globals["_EVENT_PLAYERANDMESSAGE"]._serialized_end = 1293
    _globals["_EVENT_BLOCKHIT"]._serialized_start = 1295
    _globals["_EVENT_BLOCKHIT"]._serialized_end = 1422
    _globals["_EVENT_PROJECTILEHIT"]._serialized_start = 1425
    _globals["_EVENT_PROJECTILEHIT"]._serialized_end = 1637
    _globals["_SERVERINFOREQUEST"]._serialized_start = 1648
    _globals["_SERVERINFOREQUEST"]._serialized_end = 1667
    _globals["_SERVERINFORESPONSE"]._serialized_start = 1669
    _globals["_SERVERINFORESPONSE"]._serialized_end = 1763
    _globals["_MATERIALREQUEST"]._serialized_start = 1765
    _globals["_MATERIALREQUEST"]._serialized_end = 1801
    _globals["_MATERIALRESPONSE"]._serialized_start = 1804
    _globals["_MATERIALRESPONSE"]._serialized_end = 2143
    _globals["_MATERIALRESPONSE_MATERIAL"]._serialized_start = 1915
    _globals["_MATERIALRESPONSE_MATERIAL"]._serialized_end = 2143
    _globals["_ENTITYTYPEREQUEST"]._serialized_start = 2145
    _globals["_ENTITYTYPEREQUEST"]._serialized_end = 2183
    _globals["_ENTITYTYPERESPONSE"]._serialized_start = 2186
    _globals["_ENTITYTYPERESPONSE"]._serialized_end = 2344
    _globals["_ENTITYTYPERESPONSE_ENTITYTYPE"]._serialized_start = 2298
    _globals["_ENTITYTYPERESPONSE_ENTITYTYPE"]._serialized_end = 2344
    _globals["_COMMANDREQUEST"]._serialized_start = 2346
    _globals["_COMMANDREQUEST"]._serialized_end = 2413
    _globals["_COMMANDRESPONSE"]._serialized_start = 2415
    _globals["_COMMANDRESPONSE"]._serialized_end = 2482
    _globals["_CHATPOSTREQUEST"]._serialized_start = 2484
    _globals["_CHATPOSTREQUEST"]._serialized_end = 2552
    _globals["_WORLDREQUEST"]._serialized_start = 2554
    _globals["_WORLDREQUEST"]._serialized_end = 2601
    _globals["_WORLDRESPONSE"]._serialized_start = 2603
    _globals["_WORLDRESPONSE"]._serialized_end = 2685
    _globals["_HEIGHTREQUEST"]._serialized_start = 2687
    _globals["_HEIGHTREQUEST"]._serialized_end = 2756
    _globals["_HEIGHTRESPONSE"]._serialized_start = 2758
    _globals["_HEIGHTRESPONSE"]._serialized_end = 2840
    _globals["_BLOCKREQUEST"]._serialized_start = 2842
    _globals["_BLOCKREQUEST"]._serialized_end = 2935
    _globals["_BLOCKRESPONSE"]._serialized_start = 2937
    _globals["_BLOCKRESPONSE"]._serialized_end = 3021
    _globals["_PLAYERREQUEST"]._serialized_start = 3023
    _globals["_PLAYERREQUEST"]._serialized_end = 3076
    _globals["_PLAYERRESPONSE"]._serialized_start = 3078
    _globals["_PLAYERRESPONSE"]._serialized_end = 3163
    _globals["_SPAWNEDENTITYRESPONSE"]._serialized_start = 3165
    _globals["_SPAWNEDENTITYRESPONSE"]._serialized_end = 3256
    _globals["_ENTITYREQUEST"]._serialized_start = 3259
    _globals["_ENTITYREQUEST"]._serialized_end = 3588
    _globals["_ENTITYREQUEST_SPECIFICENTITIES"]._serialized_start = 3421
    _globals["_ENTITYREQUEST_SPECIFICENTITIES"]._serialized_end = 3475
    _globals["_ENTITYREQUEST_WORLDENTITIES"]._serialized_start = 3477
    _globals["_ENTITYREQUEST_WORLDENTITIES"]._serialized_end = 3567
    _globals["_ENTITYRESPONSE"]._serialized_start = 3590
    _globals["_ENTITYRESPONSE"]._serialized_end = 3676
    _globals["_MINECRAFT"]._serialized_start = 4102
    _globals["_MINECRAFT"]._serialized_end = 5232
# @@protoc_insertion_point(module_scope)
