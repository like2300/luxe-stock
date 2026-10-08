// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $SyncMarksTable extends SyncMarks
    with TableInfo<$SyncMarksTable, SyncMarkRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncMarksTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _entityMeta = const VerificationMeta('entity');
  @override
  late final GeneratedColumn<String> entity = GeneratedColumn<String>(
    'entity',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _cursorMeta = const VerificationMeta('cursor');
  @override
  late final GeneratedColumn<String> cursor = GeneratedColumn<String>(
    'cursor',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _syncedAtMeta = const VerificationMeta(
    'syncedAt',
  );
  @override
  late final GeneratedColumn<DateTime> syncedAt = GeneratedColumn<DateTime>(
    'synced_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [entity, cursor, syncedAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_marks';
  @override
  VerificationContext validateIntegrity(
    Insertable<SyncMarkRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('entity')) {
      context.handle(
        _entityMeta,
        entity.isAcceptableOrUnknown(data['entity']!, _entityMeta),
      );
    } else if (isInserting) {
      context.missing(_entityMeta);
    }
    if (data.containsKey('cursor')) {
      context.handle(
        _cursorMeta,
        cursor.isAcceptableOrUnknown(data['cursor']!, _cursorMeta),
      );
    }
    if (data.containsKey('synced_at')) {
      context.handle(
        _syncedAtMeta,
        syncedAt.isAcceptableOrUnknown(data['synced_at']!, _syncedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {entity};
  @override
  SyncMarkRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncMarkRow(
      entity: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}entity'],
      )!,
      cursor: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}cursor'],
      )!,
      syncedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}synced_at'],
      ),
    );
  }

  @override
  $SyncMarksTable createAlias(String alias) {
    return $SyncMarksTable(attachedDatabase, alias);
  }
}

class SyncMarkRow extends DataClass implements Insertable<SyncMarkRow> {
  /// Nom d'entité du protocole : `product`, `category`, `movement`, …
  final String entity;

  /// Curseur opaque renvoyé par le dernier `pull` réussi.
  final String cursor;
  final DateTime? syncedAt;
  const SyncMarkRow({
    required this.entity,
    required this.cursor,
    this.syncedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['entity'] = Variable<String>(entity);
    map['cursor'] = Variable<String>(cursor);
    if (!nullToAbsent || syncedAt != null) {
      map['synced_at'] = Variable<DateTime>(syncedAt);
    }
    return map;
  }

  SyncMarksCompanion toCompanion(bool nullToAbsent) {
    return SyncMarksCompanion(
      entity: Value(entity),
      cursor: Value(cursor),
      syncedAt: syncedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(syncedAt),
    );
  }

  factory SyncMarkRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncMarkRow(
      entity: serializer.fromJson<String>(json['entity']),
      cursor: serializer.fromJson<String>(json['cursor']),
      syncedAt: serializer.fromJson<DateTime?>(json['syncedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'entity': serializer.toJson<String>(entity),
      'cursor': serializer.toJson<String>(cursor),
      'syncedAt': serializer.toJson<DateTime?>(syncedAt),
    };
  }

  SyncMarkRow copyWith({
    String? entity,
    String? cursor,
    Value<DateTime?> syncedAt = const Value.absent(),
  }) => SyncMarkRow(
    entity: entity ?? this.entity,
    cursor: cursor ?? this.cursor,
    syncedAt: syncedAt.present ? syncedAt.value : this.syncedAt,
  );
  SyncMarkRow copyWithCompanion(SyncMarksCompanion data) {
    return SyncMarkRow(
      entity: data.entity.present ? data.entity.value : this.entity,
      cursor: data.cursor.present ? data.cursor.value : this.cursor,
      syncedAt: data.syncedAt.present ? data.syncedAt.value : this.syncedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncMarkRow(')
          ..write('entity: $entity, ')
          ..write('cursor: $cursor, ')
          ..write('syncedAt: $syncedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(entity, cursor, syncedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncMarkRow &&
          other.entity == this.entity &&
          other.cursor == this.cursor &&
          other.syncedAt == this.syncedAt);
}

class SyncMarksCompanion extends UpdateCompanion<SyncMarkRow> {
  final Value<String> entity;
  final Value<String> cursor;
  final Value<DateTime?> syncedAt;
  final Value<int> rowid;
  const SyncMarksCompanion({
    this.entity = const Value.absent(),
    this.cursor = const Value.absent(),
    this.syncedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  SyncMarksCompanion.insert({
    required String entity,
    this.cursor = const Value.absent(),
    this.syncedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : entity = Value(entity);
  static Insertable<SyncMarkRow> custom({
    Expression<String>? entity,
    Expression<String>? cursor,
    Expression<DateTime>? syncedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (entity != null) 'entity': entity,
      if (cursor != null) 'cursor': cursor,
      if (syncedAt != null) 'synced_at': syncedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  SyncMarksCompanion copyWith({
    Value<String>? entity,
    Value<String>? cursor,
    Value<DateTime?>? syncedAt,
    Value<int>? rowid,
  }) {
    return SyncMarksCompanion(
      entity: entity ?? this.entity,
      cursor: cursor ?? this.cursor,
      syncedAt: syncedAt ?? this.syncedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (entity.present) {
      map['entity'] = Variable<String>(entity.value);
    }
    if (cursor.present) {
      map['cursor'] = Variable<String>(cursor.value);
    }
    if (syncedAt.present) {
      map['synced_at'] = Variable<DateTime>(syncedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('SyncMarksCompanion(')
          ..write('entity: $entity, ')
          ..write('cursor: $cursor, ')
          ..write('syncedAt: $syncedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $OutboxTable extends Outbox with TableInfo<$OutboxTable, OutboxRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $OutboxTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _seqMeta = const VerificationMeta('seq');
  @override
  late final GeneratedColumn<int> seq = GeneratedColumn<int>(
    'seq',
    aliasedName,
    false,
    hasAutoIncrement: true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'PRIMARY KEY AUTOINCREMENT',
    ),
  );
  static const VerificationMeta _opIdMeta = const VerificationMeta('opId');
  @override
  late final GeneratedColumn<String> opId = GeneratedColumn<String>(
    'op_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _entityMeta = const VerificationMeta('entity');
  @override
  late final GeneratedColumn<String> entity = GeneratedColumn<String>(
    'entity',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _typeMeta = const VerificationMeta('type');
  @override
  late final GeneratedColumn<String> type = GeneratedColumn<String>(
    'type',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _payloadMeta = const VerificationMeta(
    'payload',
  );
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
    'payload',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('{}'),
  );
  static const VerificationMeta _clientTimeMeta = const VerificationMeta(
    'clientTime',
  );
  @override
  late final GeneratedColumn<DateTime> clientTime = GeneratedColumn<DateTime>(
    'client_time',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _deviceIdMeta = const VerificationMeta(
    'deviceId',
  );
  @override
  late final GeneratedColumn<String> deviceId = GeneratedColumn<String>(
    'device_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _lastErrorMeta = const VerificationMeta(
    'lastError',
  );
  @override
  late final GeneratedColumn<String> lastError = GeneratedColumn<String>(
    'last_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _reasonCodeMeta = const VerificationMeta(
    'reasonCode',
  );
  @override
  late final GeneratedColumn<String> reasonCode = GeneratedColumn<String>(
    'reason_code',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _attemptsMeta = const VerificationMeta(
    'attempts',
  );
  @override
  late final GeneratedColumn<int> attempts = GeneratedColumn<int>(
    'attempts',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _lastAttemptAtMeta = const VerificationMeta(
    'lastAttemptAt',
  );
  @override
  late final GeneratedColumn<DateTime> lastAttemptAt =
      GeneratedColumn<DateTime>(
        'last_attempt_at',
        aliasedName,
        true,
        type: DriftSqlType.dateTime,
        requiredDuringInsert: false,
      );
  @override
  List<GeneratedColumn> get $columns => [
    seq,
    opId,
    entity,
    type,
    uuid,
    payload,
    clientTime,
    deviceId,
    lastError,
    reasonCode,
    attempts,
    lastAttemptAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'outbox';
  @override
  VerificationContext validateIntegrity(
    Insertable<OutboxRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('seq')) {
      context.handle(
        _seqMeta,
        seq.isAcceptableOrUnknown(data['seq']!, _seqMeta),
      );
    }
    if (data.containsKey('op_id')) {
      context.handle(
        _opIdMeta,
        opId.isAcceptableOrUnknown(data['op_id']!, _opIdMeta),
      );
    } else if (isInserting) {
      context.missing(_opIdMeta);
    }
    if (data.containsKey('entity')) {
      context.handle(
        _entityMeta,
        entity.isAcceptableOrUnknown(data['entity']!, _entityMeta),
      );
    } else if (isInserting) {
      context.missing(_entityMeta);
    }
    if (data.containsKey('type')) {
      context.handle(
        _typeMeta,
        type.isAcceptableOrUnknown(data['type']!, _typeMeta),
      );
    } else if (isInserting) {
      context.missing(_typeMeta);
    }
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    }
    if (data.containsKey('payload')) {
      context.handle(
        _payloadMeta,
        payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta),
      );
    }
    if (data.containsKey('client_time')) {
      context.handle(
        _clientTimeMeta,
        clientTime.isAcceptableOrUnknown(data['client_time']!, _clientTimeMeta),
      );
    } else if (isInserting) {
      context.missing(_clientTimeMeta);
    }
    if (data.containsKey('device_id')) {
      context.handle(
        _deviceIdMeta,
        deviceId.isAcceptableOrUnknown(data['device_id']!, _deviceIdMeta),
      );
    }
    if (data.containsKey('last_error')) {
      context.handle(
        _lastErrorMeta,
        lastError.isAcceptableOrUnknown(data['last_error']!, _lastErrorMeta),
      );
    }
    if (data.containsKey('reason_code')) {
      context.handle(
        _reasonCodeMeta,
        reasonCode.isAcceptableOrUnknown(data['reason_code']!, _reasonCodeMeta),
      );
    }
    if (data.containsKey('attempts')) {
      context.handle(
        _attemptsMeta,
        attempts.isAcceptableOrUnknown(data['attempts']!, _attemptsMeta),
      );
    }
    if (data.containsKey('last_attempt_at')) {
      context.handle(
        _lastAttemptAtMeta,
        lastAttemptAt.isAcceptableOrUnknown(
          data['last_attempt_at']!,
          _lastAttemptAtMeta,
        ),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {seq};
  @override
  OutboxRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return OutboxRow(
      seq: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}seq'],
      )!,
      opId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}op_id'],
      )!,
      entity: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}entity'],
      )!,
      type: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}type'],
      )!,
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      ),
      payload: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload'],
      )!,
      clientTime: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}client_time'],
      )!,
      deviceId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}device_id'],
      )!,
      lastError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}last_error'],
      ),
      reasonCode: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}reason_code'],
      ),
      attempts: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}attempts'],
      )!,
      lastAttemptAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}last_attempt_at'],
      ),
    );
  }

  @override
  $OutboxTable createAlias(String alias) {
    return $OutboxTable(attachedDatabase, alias);
  }
}

class OutboxRow extends DataClass implements Insertable<OutboxRow> {
  /// Ordre local : c'est la clé primaire, parce qu'elle seule est monotone.
  final int seq;

  /// Identifiant d'idempotence du protocole. Unique, mais pas primaire : deux
  /// lignes ne peuvent pas partager un `op_id`, et le `seq` doit pouvoir
  /// augmenter tout seul à chaque insertion.
  final String opId;
  final String entity;
  final String type;
  final String? uuid;

  /// Champs modifiés, au format de `payload` du protocole.
  final String payload;
  final DateTime clientTime;
  final String deviceId;

  /// Renseigné après un rejet définitif, pour l'écran de synchronisation.
  final String? lastError;
  final String? reasonCode;
  final int attempts;
  final DateTime? lastAttemptAt;
  const OutboxRow({
    required this.seq,
    required this.opId,
    required this.entity,
    required this.type,
    this.uuid,
    required this.payload,
    required this.clientTime,
    required this.deviceId,
    this.lastError,
    this.reasonCode,
    required this.attempts,
    this.lastAttemptAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['seq'] = Variable<int>(seq);
    map['op_id'] = Variable<String>(opId);
    map['entity'] = Variable<String>(entity);
    map['type'] = Variable<String>(type);
    if (!nullToAbsent || uuid != null) {
      map['uuid'] = Variable<String>(uuid);
    }
    map['payload'] = Variable<String>(payload);
    map['client_time'] = Variable<DateTime>(clientTime);
    map['device_id'] = Variable<String>(deviceId);
    if (!nullToAbsent || lastError != null) {
      map['last_error'] = Variable<String>(lastError);
    }
    if (!nullToAbsent || reasonCode != null) {
      map['reason_code'] = Variable<String>(reasonCode);
    }
    map['attempts'] = Variable<int>(attempts);
    if (!nullToAbsent || lastAttemptAt != null) {
      map['last_attempt_at'] = Variable<DateTime>(lastAttemptAt);
    }
    return map;
  }

  OutboxCompanion toCompanion(bool nullToAbsent) {
    return OutboxCompanion(
      seq: Value(seq),
      opId: Value(opId),
      entity: Value(entity),
      type: Value(type),
      uuid: uuid == null && nullToAbsent ? const Value.absent() : Value(uuid),
      payload: Value(payload),
      clientTime: Value(clientTime),
      deviceId: Value(deviceId),
      lastError: lastError == null && nullToAbsent
          ? const Value.absent()
          : Value(lastError),
      reasonCode: reasonCode == null && nullToAbsent
          ? const Value.absent()
          : Value(reasonCode),
      attempts: Value(attempts),
      lastAttemptAt: lastAttemptAt == null && nullToAbsent
          ? const Value.absent()
          : Value(lastAttemptAt),
    );
  }

  factory OutboxRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return OutboxRow(
      seq: serializer.fromJson<int>(json['seq']),
      opId: serializer.fromJson<String>(json['opId']),
      entity: serializer.fromJson<String>(json['entity']),
      type: serializer.fromJson<String>(json['type']),
      uuid: serializer.fromJson<String?>(json['uuid']),
      payload: serializer.fromJson<String>(json['payload']),
      clientTime: serializer.fromJson<DateTime>(json['clientTime']),
      deviceId: serializer.fromJson<String>(json['deviceId']),
      lastError: serializer.fromJson<String?>(json['lastError']),
      reasonCode: serializer.fromJson<String?>(json['reasonCode']),
      attempts: serializer.fromJson<int>(json['attempts']),
      lastAttemptAt: serializer.fromJson<DateTime?>(json['lastAttemptAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'seq': serializer.toJson<int>(seq),
      'opId': serializer.toJson<String>(opId),
      'entity': serializer.toJson<String>(entity),
      'type': serializer.toJson<String>(type),
      'uuid': serializer.toJson<String?>(uuid),
      'payload': serializer.toJson<String>(payload),
      'clientTime': serializer.toJson<DateTime>(clientTime),
      'deviceId': serializer.toJson<String>(deviceId),
      'lastError': serializer.toJson<String?>(lastError),
      'reasonCode': serializer.toJson<String?>(reasonCode),
      'attempts': serializer.toJson<int>(attempts),
      'lastAttemptAt': serializer.toJson<DateTime?>(lastAttemptAt),
    };
  }

  OutboxRow copyWith({
    int? seq,
    String? opId,
    String? entity,
    String? type,
    Value<String?> uuid = const Value.absent(),
    String? payload,
    DateTime? clientTime,
    String? deviceId,
    Value<String?> lastError = const Value.absent(),
    Value<String?> reasonCode = const Value.absent(),
    int? attempts,
    Value<DateTime?> lastAttemptAt = const Value.absent(),
  }) => OutboxRow(
    seq: seq ?? this.seq,
    opId: opId ?? this.opId,
    entity: entity ?? this.entity,
    type: type ?? this.type,
    uuid: uuid.present ? uuid.value : this.uuid,
    payload: payload ?? this.payload,
    clientTime: clientTime ?? this.clientTime,
    deviceId: deviceId ?? this.deviceId,
    lastError: lastError.present ? lastError.value : this.lastError,
    reasonCode: reasonCode.present ? reasonCode.value : this.reasonCode,
    attempts: attempts ?? this.attempts,
    lastAttemptAt: lastAttemptAt.present
        ? lastAttemptAt.value
        : this.lastAttemptAt,
  );
  OutboxRow copyWithCompanion(OutboxCompanion data) {
    return OutboxRow(
      seq: data.seq.present ? data.seq.value : this.seq,
      opId: data.opId.present ? data.opId.value : this.opId,
      entity: data.entity.present ? data.entity.value : this.entity,
      type: data.type.present ? data.type.value : this.type,
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      payload: data.payload.present ? data.payload.value : this.payload,
      clientTime: data.clientTime.present
          ? data.clientTime.value
          : this.clientTime,
      deviceId: data.deviceId.present ? data.deviceId.value : this.deviceId,
      lastError: data.lastError.present ? data.lastError.value : this.lastError,
      reasonCode: data.reasonCode.present
          ? data.reasonCode.value
          : this.reasonCode,
      attempts: data.attempts.present ? data.attempts.value : this.attempts,
      lastAttemptAt: data.lastAttemptAt.present
          ? data.lastAttemptAt.value
          : this.lastAttemptAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('OutboxRow(')
          ..write('seq: $seq, ')
          ..write('opId: $opId, ')
          ..write('entity: $entity, ')
          ..write('type: $type, ')
          ..write('uuid: $uuid, ')
          ..write('payload: $payload, ')
          ..write('clientTime: $clientTime, ')
          ..write('deviceId: $deviceId, ')
          ..write('lastError: $lastError, ')
          ..write('reasonCode: $reasonCode, ')
          ..write('attempts: $attempts, ')
          ..write('lastAttemptAt: $lastAttemptAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    seq,
    opId,
    entity,
    type,
    uuid,
    payload,
    clientTime,
    deviceId,
    lastError,
    reasonCode,
    attempts,
    lastAttemptAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is OutboxRow &&
          other.seq == this.seq &&
          other.opId == this.opId &&
          other.entity == this.entity &&
          other.type == this.type &&
          other.uuid == this.uuid &&
          other.payload == this.payload &&
          other.clientTime == this.clientTime &&
          other.deviceId == this.deviceId &&
          other.lastError == this.lastError &&
          other.reasonCode == this.reasonCode &&
          other.attempts == this.attempts &&
          other.lastAttemptAt == this.lastAttemptAt);
}

class OutboxCompanion extends UpdateCompanion<OutboxRow> {
  final Value<int> seq;
  final Value<String> opId;
  final Value<String> entity;
  final Value<String> type;
  final Value<String?> uuid;
  final Value<String> payload;
  final Value<DateTime> clientTime;
  final Value<String> deviceId;
  final Value<String?> lastError;
  final Value<String?> reasonCode;
  final Value<int> attempts;
  final Value<DateTime?> lastAttemptAt;
  const OutboxCompanion({
    this.seq = const Value.absent(),
    this.opId = const Value.absent(),
    this.entity = const Value.absent(),
    this.type = const Value.absent(),
    this.uuid = const Value.absent(),
    this.payload = const Value.absent(),
    this.clientTime = const Value.absent(),
    this.deviceId = const Value.absent(),
    this.lastError = const Value.absent(),
    this.reasonCode = const Value.absent(),
    this.attempts = const Value.absent(),
    this.lastAttemptAt = const Value.absent(),
  });
  OutboxCompanion.insert({
    this.seq = const Value.absent(),
    required String opId,
    required String entity,
    required String type,
    this.uuid = const Value.absent(),
    this.payload = const Value.absent(),
    required DateTime clientTime,
    this.deviceId = const Value.absent(),
    this.lastError = const Value.absent(),
    this.reasonCode = const Value.absent(),
    this.attempts = const Value.absent(),
    this.lastAttemptAt = const Value.absent(),
  }) : opId = Value(opId),
       entity = Value(entity),
       type = Value(type),
       clientTime = Value(clientTime);
  static Insertable<OutboxRow> custom({
    Expression<int>? seq,
    Expression<String>? opId,
    Expression<String>? entity,
    Expression<String>? type,
    Expression<String>? uuid,
    Expression<String>? payload,
    Expression<DateTime>? clientTime,
    Expression<String>? deviceId,
    Expression<String>? lastError,
    Expression<String>? reasonCode,
    Expression<int>? attempts,
    Expression<DateTime>? lastAttemptAt,
  }) {
    return RawValuesInsertable({
      if (seq != null) 'seq': seq,
      if (opId != null) 'op_id': opId,
      if (entity != null) 'entity': entity,
      if (type != null) 'type': type,
      if (uuid != null) 'uuid': uuid,
      if (payload != null) 'payload': payload,
      if (clientTime != null) 'client_time': clientTime,
      if (deviceId != null) 'device_id': deviceId,
      if (lastError != null) 'last_error': lastError,
      if (reasonCode != null) 'reason_code': reasonCode,
      if (attempts != null) 'attempts': attempts,
      if (lastAttemptAt != null) 'last_attempt_at': lastAttemptAt,
    });
  }

  OutboxCompanion copyWith({
    Value<int>? seq,
    Value<String>? opId,
    Value<String>? entity,
    Value<String>? type,
    Value<String?>? uuid,
    Value<String>? payload,
    Value<DateTime>? clientTime,
    Value<String>? deviceId,
    Value<String?>? lastError,
    Value<String?>? reasonCode,
    Value<int>? attempts,
    Value<DateTime?>? lastAttemptAt,
  }) {
    return OutboxCompanion(
      seq: seq ?? this.seq,
      opId: opId ?? this.opId,
      entity: entity ?? this.entity,
      type: type ?? this.type,
      uuid: uuid ?? this.uuid,
      payload: payload ?? this.payload,
      clientTime: clientTime ?? this.clientTime,
      deviceId: deviceId ?? this.deviceId,
      lastError: lastError ?? this.lastError,
      reasonCode: reasonCode ?? this.reasonCode,
      attempts: attempts ?? this.attempts,
      lastAttemptAt: lastAttemptAt ?? this.lastAttemptAt,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (seq.present) {
      map['seq'] = Variable<int>(seq.value);
    }
    if (opId.present) {
      map['op_id'] = Variable<String>(opId.value);
    }
    if (entity.present) {
      map['entity'] = Variable<String>(entity.value);
    }
    if (type.present) {
      map['type'] = Variable<String>(type.value);
    }
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (clientTime.present) {
      map['client_time'] = Variable<DateTime>(clientTime.value);
    }
    if (deviceId.present) {
      map['device_id'] = Variable<String>(deviceId.value);
    }
    if (lastError.present) {
      map['last_error'] = Variable<String>(lastError.value);
    }
    if (reasonCode.present) {
      map['reason_code'] = Variable<String>(reasonCode.value);
    }
    if (attempts.present) {
      map['attempts'] = Variable<int>(attempts.value);
    }
    if (lastAttemptAt.present) {
      map['last_attempt_at'] = Variable<DateTime>(lastAttemptAt.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('OutboxCompanion(')
          ..write('seq: $seq, ')
          ..write('opId: $opId, ')
          ..write('entity: $entity, ')
          ..write('type: $type, ')
          ..write('uuid: $uuid, ')
          ..write('payload: $payload, ')
          ..write('clientTime: $clientTime, ')
          ..write('deviceId: $deviceId, ')
          ..write('lastError: $lastError, ')
          ..write('reasonCode: $reasonCode, ')
          ..write('attempts: $attempts, ')
          ..write('lastAttemptAt: $lastAttemptAt')
          ..write(')'))
        .toString();
  }
}

class $ShopsTable extends Shops with TableInfo<$ShopsTable, ShopRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ShopsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
    'name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _currencyMeta = const VerificationMeta(
    'currency',
  );
  @override
  late final GeneratedColumn<String> currency = GeneratedColumn<String>(
    'currency',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _primaryColorMeta = const VerificationMeta(
    'primaryColor',
  );
  @override
  late final GeneratedColumn<String> primaryColor = GeneratedColumn<String>(
    'primary_color',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('#2563eb'),
  );
  static const VerificationMeta _sidebarColorMeta = const VerificationMeta(
    'sidebarColor',
  );
  @override
  late final GeneratedColumn<String> sidebarColor = GeneratedColumn<String>(
    'sidebar_color',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('#0f172a'),
  );
  static const VerificationMeta _headerColorMeta = const VerificationMeta(
    'headerColor',
  );
  @override
  late final GeneratedColumn<String> headerColor = GeneratedColumn<String>(
    'header_color',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('#0f172a'),
  );
  static const VerificationMeta _backgroundColorMeta = const VerificationMeta(
    'backgroundColor',
  );
  @override
  late final GeneratedColumn<String> backgroundColor = GeneratedColumn<String>(
    'background_color',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('#020617'),
  );
  static const VerificationMeta _scannerEnabledMeta = const VerificationMeta(
    'scannerEnabled',
  );
  @override
  late final GeneratedColumn<bool> scannerEnabled = GeneratedColumn<bool>(
    'scanner_enabled',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("scanner_enabled" IN (0, 1))',
    ),
    defaultValue: const Constant(true),
  );
  static const VerificationMeta _barcodeFieldEnabledMeta =
      const VerificationMeta('barcodeFieldEnabled');
  @override
  late final GeneratedColumn<bool> barcodeFieldEnabled = GeneratedColumn<bool>(
    'barcode_field_enabled',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("barcode_field_enabled" IN (0, 1))',
    ),
    defaultValue: const Constant(true),
  );
  static const VerificationMeta _logoUrlMeta = const VerificationMeta(
    'logoUrl',
  );
  @override
  late final GeneratedColumn<String> logoUrl = GeneratedColumn<String>(
    'logo_url',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _deletedAtMeta = const VerificationMeta(
    'deletedAt',
  );
  @override
  late final GeneratedColumn<DateTime> deletedAt = GeneratedColumn<DateTime>(
    'deleted_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    name,
    currency,
    primaryColor,
    sidebarColor,
    headerColor,
    backgroundColor,
    scannerEnabled,
    barcodeFieldEnabled,
    logoUrl,
    updatedAt,
    deletedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'shops';
  @override
  VerificationContext validateIntegrity(
    Insertable<ShopRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('name')) {
      context.handle(
        _nameMeta,
        name.isAcceptableOrUnknown(data['name']!, _nameMeta),
      );
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('currency')) {
      context.handle(
        _currencyMeta,
        currency.isAcceptableOrUnknown(data['currency']!, _currencyMeta),
      );
    }
    if (data.containsKey('primary_color')) {
      context.handle(
        _primaryColorMeta,
        primaryColor.isAcceptableOrUnknown(
          data['primary_color']!,
          _primaryColorMeta,
        ),
      );
    }
    if (data.containsKey('sidebar_color')) {
      context.handle(
        _sidebarColorMeta,
        sidebarColor.isAcceptableOrUnknown(
          data['sidebar_color']!,
          _sidebarColorMeta,
        ),
      );
    }
    if (data.containsKey('header_color')) {
      context.handle(
        _headerColorMeta,
        headerColor.isAcceptableOrUnknown(
          data['header_color']!,
          _headerColorMeta,
        ),
      );
    }
    if (data.containsKey('background_color')) {
      context.handle(
        _backgroundColorMeta,
        backgroundColor.isAcceptableOrUnknown(
          data['background_color']!,
          _backgroundColorMeta,
        ),
      );
    }
    if (data.containsKey('scanner_enabled')) {
      context.handle(
        _scannerEnabledMeta,
        scannerEnabled.isAcceptableOrUnknown(
          data['scanner_enabled']!,
          _scannerEnabledMeta,
        ),
      );
    }
    if (data.containsKey('barcode_field_enabled')) {
      context.handle(
        _barcodeFieldEnabledMeta,
        barcodeFieldEnabled.isAcceptableOrUnknown(
          data['barcode_field_enabled']!,
          _barcodeFieldEnabledMeta,
        ),
      );
    }
    if (data.containsKey('logo_url')) {
      context.handle(
        _logoUrlMeta,
        logoUrl.isAcceptableOrUnknown(data['logo_url']!, _logoUrlMeta),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    if (data.containsKey('deleted_at')) {
      context.handle(
        _deletedAtMeta,
        deletedAt.isAcceptableOrUnknown(data['deleted_at']!, _deletedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  ShopRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return ShopRow(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      name: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}name'],
      )!,
      currency: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}currency'],
      )!,
      primaryColor: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}primary_color'],
      )!,
      sidebarColor: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sidebar_color'],
      )!,
      headerColor: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}header_color'],
      )!,
      backgroundColor: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}background_color'],
      )!,
      scannerEnabled: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}scanner_enabled'],
      )!,
      barcodeFieldEnabled: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}barcode_field_enabled'],
      )!,
      logoUrl: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}logo_url'],
      ),
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      ),
      deletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}deleted_at'],
      ),
    );
  }

  @override
  $ShopsTable createAlias(String alias) {
    return $ShopsTable(attachedDatabase, alias);
  }
}

class ShopRow extends DataClass implements Insertable<ShopRow> {
  final String uuid;
  final String name;
  final String currency;
  final String primaryColor;
  final String sidebarColor;
  final String headerColor;
  final String backgroundColor;
  final bool scannerEnabled;
  final bool barcodeFieldEnabled;
  final String? logoUrl;
  final DateTime? updatedAt;
  final DateTime? deletedAt;
  const ShopRow({
    required this.uuid,
    required this.name,
    required this.currency,
    required this.primaryColor,
    required this.sidebarColor,
    required this.headerColor,
    required this.backgroundColor,
    required this.scannerEnabled,
    required this.barcodeFieldEnabled,
    this.logoUrl,
    this.updatedAt,
    this.deletedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['name'] = Variable<String>(name);
    map['currency'] = Variable<String>(currency);
    map['primary_color'] = Variable<String>(primaryColor);
    map['sidebar_color'] = Variable<String>(sidebarColor);
    map['header_color'] = Variable<String>(headerColor);
    map['background_color'] = Variable<String>(backgroundColor);
    map['scanner_enabled'] = Variable<bool>(scannerEnabled);
    map['barcode_field_enabled'] = Variable<bool>(barcodeFieldEnabled);
    if (!nullToAbsent || logoUrl != null) {
      map['logo_url'] = Variable<String>(logoUrl);
    }
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    if (!nullToAbsent || deletedAt != null) {
      map['deleted_at'] = Variable<DateTime>(deletedAt);
    }
    return map;
  }

  ShopsCompanion toCompanion(bool nullToAbsent) {
    return ShopsCompanion(
      uuid: Value(uuid),
      name: Value(name),
      currency: Value(currency),
      primaryColor: Value(primaryColor),
      sidebarColor: Value(sidebarColor),
      headerColor: Value(headerColor),
      backgroundColor: Value(backgroundColor),
      scannerEnabled: Value(scannerEnabled),
      barcodeFieldEnabled: Value(barcodeFieldEnabled),
      logoUrl: logoUrl == null && nullToAbsent
          ? const Value.absent()
          : Value(logoUrl),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
      deletedAt: deletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(deletedAt),
    );
  }

  factory ShopRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return ShopRow(
      uuid: serializer.fromJson<String>(json['uuid']),
      name: serializer.fromJson<String>(json['name']),
      currency: serializer.fromJson<String>(json['currency']),
      primaryColor: serializer.fromJson<String>(json['primaryColor']),
      sidebarColor: serializer.fromJson<String>(json['sidebarColor']),
      headerColor: serializer.fromJson<String>(json['headerColor']),
      backgroundColor: serializer.fromJson<String>(json['backgroundColor']),
      scannerEnabled: serializer.fromJson<bool>(json['scannerEnabled']),
      barcodeFieldEnabled: serializer.fromJson<bool>(
        json['barcodeFieldEnabled'],
      ),
      logoUrl: serializer.fromJson<String?>(json['logoUrl']),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
      deletedAt: serializer.fromJson<DateTime?>(json['deletedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'name': serializer.toJson<String>(name),
      'currency': serializer.toJson<String>(currency),
      'primaryColor': serializer.toJson<String>(primaryColor),
      'sidebarColor': serializer.toJson<String>(sidebarColor),
      'headerColor': serializer.toJson<String>(headerColor),
      'backgroundColor': serializer.toJson<String>(backgroundColor),
      'scannerEnabled': serializer.toJson<bool>(scannerEnabled),
      'barcodeFieldEnabled': serializer.toJson<bool>(barcodeFieldEnabled),
      'logoUrl': serializer.toJson<String?>(logoUrl),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
      'deletedAt': serializer.toJson<DateTime?>(deletedAt),
    };
  }

  ShopRow copyWith({
    String? uuid,
    String? name,
    String? currency,
    String? primaryColor,
    String? sidebarColor,
    String? headerColor,
    String? backgroundColor,
    bool? scannerEnabled,
    bool? barcodeFieldEnabled,
    Value<String?> logoUrl = const Value.absent(),
    Value<DateTime?> updatedAt = const Value.absent(),
    Value<DateTime?> deletedAt = const Value.absent(),
  }) => ShopRow(
    uuid: uuid ?? this.uuid,
    name: name ?? this.name,
    currency: currency ?? this.currency,
    primaryColor: primaryColor ?? this.primaryColor,
    sidebarColor: sidebarColor ?? this.sidebarColor,
    headerColor: headerColor ?? this.headerColor,
    backgroundColor: backgroundColor ?? this.backgroundColor,
    scannerEnabled: scannerEnabled ?? this.scannerEnabled,
    barcodeFieldEnabled: barcodeFieldEnabled ?? this.barcodeFieldEnabled,
    logoUrl: logoUrl.present ? logoUrl.value : this.logoUrl,
    updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
    deletedAt: deletedAt.present ? deletedAt.value : this.deletedAt,
  );
  ShopRow copyWithCompanion(ShopsCompanion data) {
    return ShopRow(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      name: data.name.present ? data.name.value : this.name,
      currency: data.currency.present ? data.currency.value : this.currency,
      primaryColor: data.primaryColor.present
          ? data.primaryColor.value
          : this.primaryColor,
      sidebarColor: data.sidebarColor.present
          ? data.sidebarColor.value
          : this.sidebarColor,
      headerColor: data.headerColor.present
          ? data.headerColor.value
          : this.headerColor,
      backgroundColor: data.backgroundColor.present
          ? data.backgroundColor.value
          : this.backgroundColor,
      scannerEnabled: data.scannerEnabled.present
          ? data.scannerEnabled.value
          : this.scannerEnabled,
      barcodeFieldEnabled: data.barcodeFieldEnabled.present
          ? data.barcodeFieldEnabled.value
          : this.barcodeFieldEnabled,
      logoUrl: data.logoUrl.present ? data.logoUrl.value : this.logoUrl,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      deletedAt: data.deletedAt.present ? data.deletedAt.value : this.deletedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('ShopRow(')
          ..write('uuid: $uuid, ')
          ..write('name: $name, ')
          ..write('currency: $currency, ')
          ..write('primaryColor: $primaryColor, ')
          ..write('sidebarColor: $sidebarColor, ')
          ..write('headerColor: $headerColor, ')
          ..write('backgroundColor: $backgroundColor, ')
          ..write('scannerEnabled: $scannerEnabled, ')
          ..write('barcodeFieldEnabled: $barcodeFieldEnabled, ')
          ..write('logoUrl: $logoUrl, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    name,
    currency,
    primaryColor,
    sidebarColor,
    headerColor,
    backgroundColor,
    scannerEnabled,
    barcodeFieldEnabled,
    logoUrl,
    updatedAt,
    deletedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is ShopRow &&
          other.uuid == this.uuid &&
          other.name == this.name &&
          other.currency == this.currency &&
          other.primaryColor == this.primaryColor &&
          other.sidebarColor == this.sidebarColor &&
          other.headerColor == this.headerColor &&
          other.backgroundColor == this.backgroundColor &&
          other.scannerEnabled == this.scannerEnabled &&
          other.barcodeFieldEnabled == this.barcodeFieldEnabled &&
          other.logoUrl == this.logoUrl &&
          other.updatedAt == this.updatedAt &&
          other.deletedAt == this.deletedAt);
}

class ShopsCompanion extends UpdateCompanion<ShopRow> {
  final Value<String> uuid;
  final Value<String> name;
  final Value<String> currency;
  final Value<String> primaryColor;
  final Value<String> sidebarColor;
  final Value<String> headerColor;
  final Value<String> backgroundColor;
  final Value<bool> scannerEnabled;
  final Value<bool> barcodeFieldEnabled;
  final Value<String?> logoUrl;
  final Value<DateTime?> updatedAt;
  final Value<DateTime?> deletedAt;
  final Value<int> rowid;
  const ShopsCompanion({
    this.uuid = const Value.absent(),
    this.name = const Value.absent(),
    this.currency = const Value.absent(),
    this.primaryColor = const Value.absent(),
    this.sidebarColor = const Value.absent(),
    this.headerColor = const Value.absent(),
    this.backgroundColor = const Value.absent(),
    this.scannerEnabled = const Value.absent(),
    this.barcodeFieldEnabled = const Value.absent(),
    this.logoUrl = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ShopsCompanion.insert({
    required String uuid,
    required String name,
    this.currency = const Value.absent(),
    this.primaryColor = const Value.absent(),
    this.sidebarColor = const Value.absent(),
    this.headerColor = const Value.absent(),
    this.backgroundColor = const Value.absent(),
    this.scannerEnabled = const Value.absent(),
    this.barcodeFieldEnabled = const Value.absent(),
    this.logoUrl = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       name = Value(name);
  static Insertable<ShopRow> custom({
    Expression<String>? uuid,
    Expression<String>? name,
    Expression<String>? currency,
    Expression<String>? primaryColor,
    Expression<String>? sidebarColor,
    Expression<String>? headerColor,
    Expression<String>? backgroundColor,
    Expression<bool>? scannerEnabled,
    Expression<bool>? barcodeFieldEnabled,
    Expression<String>? logoUrl,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? deletedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (name != null) 'name': name,
      if (currency != null) 'currency': currency,
      if (primaryColor != null) 'primary_color': primaryColor,
      if (sidebarColor != null) 'sidebar_color': sidebarColor,
      if (headerColor != null) 'header_color': headerColor,
      if (backgroundColor != null) 'background_color': backgroundColor,
      if (scannerEnabled != null) 'scanner_enabled': scannerEnabled,
      if (barcodeFieldEnabled != null)
        'barcode_field_enabled': barcodeFieldEnabled,
      if (logoUrl != null) 'logo_url': logoUrl,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (deletedAt != null) 'deleted_at': deletedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ShopsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? name,
    Value<String>? currency,
    Value<String>? primaryColor,
    Value<String>? sidebarColor,
    Value<String>? headerColor,
    Value<String>? backgroundColor,
    Value<bool>? scannerEnabled,
    Value<bool>? barcodeFieldEnabled,
    Value<String?>? logoUrl,
    Value<DateTime?>? updatedAt,
    Value<DateTime?>? deletedAt,
    Value<int>? rowid,
  }) {
    return ShopsCompanion(
      uuid: uuid ?? this.uuid,
      name: name ?? this.name,
      currency: currency ?? this.currency,
      primaryColor: primaryColor ?? this.primaryColor,
      sidebarColor: sidebarColor ?? this.sidebarColor,
      headerColor: headerColor ?? this.headerColor,
      backgroundColor: backgroundColor ?? this.backgroundColor,
      scannerEnabled: scannerEnabled ?? this.scannerEnabled,
      barcodeFieldEnabled: barcodeFieldEnabled ?? this.barcodeFieldEnabled,
      logoUrl: logoUrl ?? this.logoUrl,
      updatedAt: updatedAt ?? this.updatedAt,
      deletedAt: deletedAt ?? this.deletedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (currency.present) {
      map['currency'] = Variable<String>(currency.value);
    }
    if (primaryColor.present) {
      map['primary_color'] = Variable<String>(primaryColor.value);
    }
    if (sidebarColor.present) {
      map['sidebar_color'] = Variable<String>(sidebarColor.value);
    }
    if (headerColor.present) {
      map['header_color'] = Variable<String>(headerColor.value);
    }
    if (backgroundColor.present) {
      map['background_color'] = Variable<String>(backgroundColor.value);
    }
    if (scannerEnabled.present) {
      map['scanner_enabled'] = Variable<bool>(scannerEnabled.value);
    }
    if (barcodeFieldEnabled.present) {
      map['barcode_field_enabled'] = Variable<bool>(barcodeFieldEnabled.value);
    }
    if (logoUrl.present) {
      map['logo_url'] = Variable<String>(logoUrl.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (deletedAt.present) {
      map['deleted_at'] = Variable<DateTime>(deletedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ShopsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('name: $name, ')
          ..write('currency: $currency, ')
          ..write('primaryColor: $primaryColor, ')
          ..write('sidebarColor: $sidebarColor, ')
          ..write('headerColor: $headerColor, ')
          ..write('backgroundColor: $backgroundColor, ')
          ..write('scannerEnabled: $scannerEnabled, ')
          ..write('barcodeFieldEnabled: $barcodeFieldEnabled, ')
          ..write('logoUrl: $logoUrl, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CategoriesTable extends Categories
    with TableInfo<$CategoriesTable, CategoryRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CategoriesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
    'name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _productCountMeta = const VerificationMeta(
    'productCount',
  );
  @override
  late final GeneratedColumn<int> productCount = GeneratedColumn<int>(
    'product_count',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _deletedAtMeta = const VerificationMeta(
    'deletedAt',
  );
  @override
  late final GeneratedColumn<DateTime> deletedAt = GeneratedColumn<DateTime>(
    'deleted_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    name,
    productCount,
    updatedAt,
    deletedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'categories';
  @override
  VerificationContext validateIntegrity(
    Insertable<CategoryRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('name')) {
      context.handle(
        _nameMeta,
        name.isAcceptableOrUnknown(data['name']!, _nameMeta),
      );
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('product_count')) {
      context.handle(
        _productCountMeta,
        productCount.isAcceptableOrUnknown(
          data['product_count']!,
          _productCountMeta,
        ),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    if (data.containsKey('deleted_at')) {
      context.handle(
        _deletedAtMeta,
        deletedAt.isAcceptableOrUnknown(data['deleted_at']!, _deletedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  CategoryRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CategoryRow(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      name: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}name'],
      )!,
      productCount: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}product_count'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      ),
      deletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}deleted_at'],
      ),
    );
  }

  @override
  $CategoriesTable createAlias(String alias) {
    return $CategoriesTable(attachedDatabase, alias);
  }
}

class CategoryRow extends DataClass implements Insertable<CategoryRow> {
  final String uuid;
  final String name;
  final int productCount;
  final DateTime? updatedAt;
  final DateTime? deletedAt;
  const CategoryRow({
    required this.uuid,
    required this.name,
    required this.productCount,
    this.updatedAt,
    this.deletedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['name'] = Variable<String>(name);
    map['product_count'] = Variable<int>(productCount);
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    if (!nullToAbsent || deletedAt != null) {
      map['deleted_at'] = Variable<DateTime>(deletedAt);
    }
    return map;
  }

  CategoriesCompanion toCompanion(bool nullToAbsent) {
    return CategoriesCompanion(
      uuid: Value(uuid),
      name: Value(name),
      productCount: Value(productCount),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
      deletedAt: deletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(deletedAt),
    );
  }

  factory CategoryRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CategoryRow(
      uuid: serializer.fromJson<String>(json['uuid']),
      name: serializer.fromJson<String>(json['name']),
      productCount: serializer.fromJson<int>(json['productCount']),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
      deletedAt: serializer.fromJson<DateTime?>(json['deletedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'name': serializer.toJson<String>(name),
      'productCount': serializer.toJson<int>(productCount),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
      'deletedAt': serializer.toJson<DateTime?>(deletedAt),
    };
  }

  CategoryRow copyWith({
    String? uuid,
    String? name,
    int? productCount,
    Value<DateTime?> updatedAt = const Value.absent(),
    Value<DateTime?> deletedAt = const Value.absent(),
  }) => CategoryRow(
    uuid: uuid ?? this.uuid,
    name: name ?? this.name,
    productCount: productCount ?? this.productCount,
    updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
    deletedAt: deletedAt.present ? deletedAt.value : this.deletedAt,
  );
  CategoryRow copyWithCompanion(CategoriesCompanion data) {
    return CategoryRow(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      name: data.name.present ? data.name.value : this.name,
      productCount: data.productCount.present
          ? data.productCount.value
          : this.productCount,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      deletedAt: data.deletedAt.present ? data.deletedAt.value : this.deletedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CategoryRow(')
          ..write('uuid: $uuid, ')
          ..write('name: $name, ')
          ..write('productCount: $productCount, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(uuid, name, productCount, updatedAt, deletedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CategoryRow &&
          other.uuid == this.uuid &&
          other.name == this.name &&
          other.productCount == this.productCount &&
          other.updatedAt == this.updatedAt &&
          other.deletedAt == this.deletedAt);
}

class CategoriesCompanion extends UpdateCompanion<CategoryRow> {
  final Value<String> uuid;
  final Value<String> name;
  final Value<int> productCount;
  final Value<DateTime?> updatedAt;
  final Value<DateTime?> deletedAt;
  final Value<int> rowid;
  const CategoriesCompanion({
    this.uuid = const Value.absent(),
    this.name = const Value.absent(),
    this.productCount = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CategoriesCompanion.insert({
    required String uuid,
    required String name,
    this.productCount = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       name = Value(name);
  static Insertable<CategoryRow> custom({
    Expression<String>? uuid,
    Expression<String>? name,
    Expression<int>? productCount,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? deletedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (name != null) 'name': name,
      if (productCount != null) 'product_count': productCount,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (deletedAt != null) 'deleted_at': deletedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CategoriesCompanion copyWith({
    Value<String>? uuid,
    Value<String>? name,
    Value<int>? productCount,
    Value<DateTime?>? updatedAt,
    Value<DateTime?>? deletedAt,
    Value<int>? rowid,
  }) {
    return CategoriesCompanion(
      uuid: uuid ?? this.uuid,
      name: name ?? this.name,
      productCount: productCount ?? this.productCount,
      updatedAt: updatedAt ?? this.updatedAt,
      deletedAt: deletedAt ?? this.deletedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (productCount.present) {
      map['product_count'] = Variable<int>(productCount.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (deletedAt.present) {
      map['deleted_at'] = Variable<DateTime>(deletedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CategoriesCompanion(')
          ..write('uuid: $uuid, ')
          ..write('name: $name, ')
          ..write('productCount: $productCount, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ProductsTable extends Products
    with TableInfo<$ProductsTable, ProductRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ProductsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _nameMeta = const VerificationMeta('name');
  @override
  late final GeneratedColumn<String> name = GeneratedColumn<String>(
    'name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _skuMeta = const VerificationMeta('sku');
  @override
  late final GeneratedColumn<String> sku = GeneratedColumn<String>(
    'sku',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _barcodeMeta = const VerificationMeta(
    'barcode',
  );
  @override
  late final GeneratedColumn<String> barcode = GeneratedColumn<String>(
    'barcode',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _categoryUuidMeta = const VerificationMeta(
    'categoryUuid',
  );
  @override
  late final GeneratedColumn<String> categoryUuid = GeneratedColumn<String>(
    'category_uuid',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _categoryNameMeta = const VerificationMeta(
    'categoryName',
  );
  @override
  late final GeneratedColumn<String> categoryName = GeneratedColumn<String>(
    'category_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _quantityMeta = const VerificationMeta(
    'quantity',
  );
  @override
  late final GeneratedColumn<int> quantity = GeneratedColumn<int>(
    'quantity',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _alertThresholdMeta = const VerificationMeta(
    'alertThreshold',
  );
  @override
  late final GeneratedColumn<int> alertThreshold = GeneratedColumn<int>(
    'alert_threshold',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _salePriceMeta = const VerificationMeta(
    'salePrice',
  );
  @override
  late final GeneratedColumn<String> salePrice = GeneratedColumn<String>(
    'sale_price',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('0'),
  );
  static const VerificationMeta _costPriceMeta = const VerificationMeta(
    'costPrice',
  );
  @override
  late final GeneratedColumn<String> costPrice = GeneratedColumn<String>(
    'cost_price',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('0'),
  );
  static const VerificationMeta _currencyMeta = const VerificationMeta(
    'currency',
  );
  @override
  late final GeneratedColumn<String> currency = GeneratedColumn<String>(
    'currency',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _descriptionMeta = const VerificationMeta(
    'description',
  );
  @override
  late final GeneratedColumn<String> description = GeneratedColumn<String>(
    'description',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _levelMeta = const VerificationMeta('level');
  @override
  late final GeneratedColumn<String> level = GeneratedColumn<String>(
    'level',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('ok'),
  );
  static const VerificationMeta _hasPendingOpMeta = const VerificationMeta(
    'hasPendingOp',
  );
  @override
  late final GeneratedColumn<bool> hasPendingOp = GeneratedColumn<bool>(
    'has_pending_op',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("has_pending_op" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _deletedAtMeta = const VerificationMeta(
    'deletedAt',
  );
  @override
  late final GeneratedColumn<DateTime> deletedAt = GeneratedColumn<DateTime>(
    'deleted_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    name,
    sku,
    barcode,
    categoryUuid,
    categoryName,
    quantity,
    alertThreshold,
    salePrice,
    costPrice,
    currency,
    description,
    level,
    hasPendingOp,
    updatedAt,
    deletedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'products';
  @override
  VerificationContext validateIntegrity(
    Insertable<ProductRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('name')) {
      context.handle(
        _nameMeta,
        name.isAcceptableOrUnknown(data['name']!, _nameMeta),
      );
    } else if (isInserting) {
      context.missing(_nameMeta);
    }
    if (data.containsKey('sku')) {
      context.handle(
        _skuMeta,
        sku.isAcceptableOrUnknown(data['sku']!, _skuMeta),
      );
    }
    if (data.containsKey('barcode')) {
      context.handle(
        _barcodeMeta,
        barcode.isAcceptableOrUnknown(data['barcode']!, _barcodeMeta),
      );
    }
    if (data.containsKey('category_uuid')) {
      context.handle(
        _categoryUuidMeta,
        categoryUuid.isAcceptableOrUnknown(
          data['category_uuid']!,
          _categoryUuidMeta,
        ),
      );
    }
    if (data.containsKey('category_name')) {
      context.handle(
        _categoryNameMeta,
        categoryName.isAcceptableOrUnknown(
          data['category_name']!,
          _categoryNameMeta,
        ),
      );
    }
    if (data.containsKey('quantity')) {
      context.handle(
        _quantityMeta,
        quantity.isAcceptableOrUnknown(data['quantity']!, _quantityMeta),
      );
    }
    if (data.containsKey('alert_threshold')) {
      context.handle(
        _alertThresholdMeta,
        alertThreshold.isAcceptableOrUnknown(
          data['alert_threshold']!,
          _alertThresholdMeta,
        ),
      );
    }
    if (data.containsKey('sale_price')) {
      context.handle(
        _salePriceMeta,
        salePrice.isAcceptableOrUnknown(data['sale_price']!, _salePriceMeta),
      );
    }
    if (data.containsKey('cost_price')) {
      context.handle(
        _costPriceMeta,
        costPrice.isAcceptableOrUnknown(data['cost_price']!, _costPriceMeta),
      );
    }
    if (data.containsKey('currency')) {
      context.handle(
        _currencyMeta,
        currency.isAcceptableOrUnknown(data['currency']!, _currencyMeta),
      );
    }
    if (data.containsKey('description')) {
      context.handle(
        _descriptionMeta,
        description.isAcceptableOrUnknown(
          data['description']!,
          _descriptionMeta,
        ),
      );
    }
    if (data.containsKey('level')) {
      context.handle(
        _levelMeta,
        level.isAcceptableOrUnknown(data['level']!, _levelMeta),
      );
    }
    if (data.containsKey('has_pending_op')) {
      context.handle(
        _hasPendingOpMeta,
        hasPendingOp.isAcceptableOrUnknown(
          data['has_pending_op']!,
          _hasPendingOpMeta,
        ),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    if (data.containsKey('deleted_at')) {
      context.handle(
        _deletedAtMeta,
        deletedAt.isAcceptableOrUnknown(data['deleted_at']!, _deletedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  ProductRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return ProductRow(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      name: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}name'],
      )!,
      sku: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sku'],
      )!,
      barcode: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}barcode'],
      )!,
      categoryUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}category_uuid'],
      ),
      categoryName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}category_name'],
      )!,
      quantity: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}quantity'],
      )!,
      alertThreshold: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}alert_threshold'],
      )!,
      salePrice: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sale_price'],
      )!,
      costPrice: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}cost_price'],
      )!,
      currency: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}currency'],
      )!,
      description: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}description'],
      )!,
      level: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}level'],
      )!,
      hasPendingOp: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}has_pending_op'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      ),
      deletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}deleted_at'],
      ),
    );
  }

  @override
  $ProductsTable createAlias(String alias) {
    return $ProductsTable(attachedDatabase, alias);
  }
}

class ProductRow extends DataClass implements Insertable<ProductRow> {
  final String uuid;
  final String name;
  final String sku;
  final String barcode;

  /// Clé étrangère locale : `Categories.uuid`.
  final String? categoryUuid;
  final String categoryName;
  final int quantity;
  final int alertThreshold;
  final String salePrice;
  final String costPrice;
  final String currency;
  final String description;

  /// `rupture`, `bas` ou `ok`, recalculé localement pour ne pas dépendre du serveur.
  final String level;

  /// Vrai tant que la ligne a une opération locale en attente : le pull ne doit
  /// alors pas l'écraser, sinon la saisie hors ligne disparaît avant d'être envoyée.
  final bool hasPendingOp;
  final DateTime? updatedAt;
  final DateTime? deletedAt;
  const ProductRow({
    required this.uuid,
    required this.name,
    required this.sku,
    required this.barcode,
    this.categoryUuid,
    required this.categoryName,
    required this.quantity,
    required this.alertThreshold,
    required this.salePrice,
    required this.costPrice,
    required this.currency,
    required this.description,
    required this.level,
    required this.hasPendingOp,
    this.updatedAt,
    this.deletedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['name'] = Variable<String>(name);
    map['sku'] = Variable<String>(sku);
    map['barcode'] = Variable<String>(barcode);
    if (!nullToAbsent || categoryUuid != null) {
      map['category_uuid'] = Variable<String>(categoryUuid);
    }
    map['category_name'] = Variable<String>(categoryName);
    map['quantity'] = Variable<int>(quantity);
    map['alert_threshold'] = Variable<int>(alertThreshold);
    map['sale_price'] = Variable<String>(salePrice);
    map['cost_price'] = Variable<String>(costPrice);
    map['currency'] = Variable<String>(currency);
    map['description'] = Variable<String>(description);
    map['level'] = Variable<String>(level);
    map['has_pending_op'] = Variable<bool>(hasPendingOp);
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    if (!nullToAbsent || deletedAt != null) {
      map['deleted_at'] = Variable<DateTime>(deletedAt);
    }
    return map;
  }

  ProductsCompanion toCompanion(bool nullToAbsent) {
    return ProductsCompanion(
      uuid: Value(uuid),
      name: Value(name),
      sku: Value(sku),
      barcode: Value(barcode),
      categoryUuid: categoryUuid == null && nullToAbsent
          ? const Value.absent()
          : Value(categoryUuid),
      categoryName: Value(categoryName),
      quantity: Value(quantity),
      alertThreshold: Value(alertThreshold),
      salePrice: Value(salePrice),
      costPrice: Value(costPrice),
      currency: Value(currency),
      description: Value(description),
      level: Value(level),
      hasPendingOp: Value(hasPendingOp),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
      deletedAt: deletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(deletedAt),
    );
  }

  factory ProductRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return ProductRow(
      uuid: serializer.fromJson<String>(json['uuid']),
      name: serializer.fromJson<String>(json['name']),
      sku: serializer.fromJson<String>(json['sku']),
      barcode: serializer.fromJson<String>(json['barcode']),
      categoryUuid: serializer.fromJson<String?>(json['categoryUuid']),
      categoryName: serializer.fromJson<String>(json['categoryName']),
      quantity: serializer.fromJson<int>(json['quantity']),
      alertThreshold: serializer.fromJson<int>(json['alertThreshold']),
      salePrice: serializer.fromJson<String>(json['salePrice']),
      costPrice: serializer.fromJson<String>(json['costPrice']),
      currency: serializer.fromJson<String>(json['currency']),
      description: serializer.fromJson<String>(json['description']),
      level: serializer.fromJson<String>(json['level']),
      hasPendingOp: serializer.fromJson<bool>(json['hasPendingOp']),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
      deletedAt: serializer.fromJson<DateTime?>(json['deletedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'name': serializer.toJson<String>(name),
      'sku': serializer.toJson<String>(sku),
      'barcode': serializer.toJson<String>(barcode),
      'categoryUuid': serializer.toJson<String?>(categoryUuid),
      'categoryName': serializer.toJson<String>(categoryName),
      'quantity': serializer.toJson<int>(quantity),
      'alertThreshold': serializer.toJson<int>(alertThreshold),
      'salePrice': serializer.toJson<String>(salePrice),
      'costPrice': serializer.toJson<String>(costPrice),
      'currency': serializer.toJson<String>(currency),
      'description': serializer.toJson<String>(description),
      'level': serializer.toJson<String>(level),
      'hasPendingOp': serializer.toJson<bool>(hasPendingOp),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
      'deletedAt': serializer.toJson<DateTime?>(deletedAt),
    };
  }

  ProductRow copyWith({
    String? uuid,
    String? name,
    String? sku,
    String? barcode,
    Value<String?> categoryUuid = const Value.absent(),
    String? categoryName,
    int? quantity,
    int? alertThreshold,
    String? salePrice,
    String? costPrice,
    String? currency,
    String? description,
    String? level,
    bool? hasPendingOp,
    Value<DateTime?> updatedAt = const Value.absent(),
    Value<DateTime?> deletedAt = const Value.absent(),
  }) => ProductRow(
    uuid: uuid ?? this.uuid,
    name: name ?? this.name,
    sku: sku ?? this.sku,
    barcode: barcode ?? this.barcode,
    categoryUuid: categoryUuid.present ? categoryUuid.value : this.categoryUuid,
    categoryName: categoryName ?? this.categoryName,
    quantity: quantity ?? this.quantity,
    alertThreshold: alertThreshold ?? this.alertThreshold,
    salePrice: salePrice ?? this.salePrice,
    costPrice: costPrice ?? this.costPrice,
    currency: currency ?? this.currency,
    description: description ?? this.description,
    level: level ?? this.level,
    hasPendingOp: hasPendingOp ?? this.hasPendingOp,
    updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
    deletedAt: deletedAt.present ? deletedAt.value : this.deletedAt,
  );
  ProductRow copyWithCompanion(ProductsCompanion data) {
    return ProductRow(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      name: data.name.present ? data.name.value : this.name,
      sku: data.sku.present ? data.sku.value : this.sku,
      barcode: data.barcode.present ? data.barcode.value : this.barcode,
      categoryUuid: data.categoryUuid.present
          ? data.categoryUuid.value
          : this.categoryUuid,
      categoryName: data.categoryName.present
          ? data.categoryName.value
          : this.categoryName,
      quantity: data.quantity.present ? data.quantity.value : this.quantity,
      alertThreshold: data.alertThreshold.present
          ? data.alertThreshold.value
          : this.alertThreshold,
      salePrice: data.salePrice.present ? data.salePrice.value : this.salePrice,
      costPrice: data.costPrice.present ? data.costPrice.value : this.costPrice,
      currency: data.currency.present ? data.currency.value : this.currency,
      description: data.description.present
          ? data.description.value
          : this.description,
      level: data.level.present ? data.level.value : this.level,
      hasPendingOp: data.hasPendingOp.present
          ? data.hasPendingOp.value
          : this.hasPendingOp,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      deletedAt: data.deletedAt.present ? data.deletedAt.value : this.deletedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('ProductRow(')
          ..write('uuid: $uuid, ')
          ..write('name: $name, ')
          ..write('sku: $sku, ')
          ..write('barcode: $barcode, ')
          ..write('categoryUuid: $categoryUuid, ')
          ..write('categoryName: $categoryName, ')
          ..write('quantity: $quantity, ')
          ..write('alertThreshold: $alertThreshold, ')
          ..write('salePrice: $salePrice, ')
          ..write('costPrice: $costPrice, ')
          ..write('currency: $currency, ')
          ..write('description: $description, ')
          ..write('level: $level, ')
          ..write('hasPendingOp: $hasPendingOp, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    name,
    sku,
    barcode,
    categoryUuid,
    categoryName,
    quantity,
    alertThreshold,
    salePrice,
    costPrice,
    currency,
    description,
    level,
    hasPendingOp,
    updatedAt,
    deletedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is ProductRow &&
          other.uuid == this.uuid &&
          other.name == this.name &&
          other.sku == this.sku &&
          other.barcode == this.barcode &&
          other.categoryUuid == this.categoryUuid &&
          other.categoryName == this.categoryName &&
          other.quantity == this.quantity &&
          other.alertThreshold == this.alertThreshold &&
          other.salePrice == this.salePrice &&
          other.costPrice == this.costPrice &&
          other.currency == this.currency &&
          other.description == this.description &&
          other.level == this.level &&
          other.hasPendingOp == this.hasPendingOp &&
          other.updatedAt == this.updatedAt &&
          other.deletedAt == this.deletedAt);
}

class ProductsCompanion extends UpdateCompanion<ProductRow> {
  final Value<String> uuid;
  final Value<String> name;
  final Value<String> sku;
  final Value<String> barcode;
  final Value<String?> categoryUuid;
  final Value<String> categoryName;
  final Value<int> quantity;
  final Value<int> alertThreshold;
  final Value<String> salePrice;
  final Value<String> costPrice;
  final Value<String> currency;
  final Value<String> description;
  final Value<String> level;
  final Value<bool> hasPendingOp;
  final Value<DateTime?> updatedAt;
  final Value<DateTime?> deletedAt;
  final Value<int> rowid;
  const ProductsCompanion({
    this.uuid = const Value.absent(),
    this.name = const Value.absent(),
    this.sku = const Value.absent(),
    this.barcode = const Value.absent(),
    this.categoryUuid = const Value.absent(),
    this.categoryName = const Value.absent(),
    this.quantity = const Value.absent(),
    this.alertThreshold = const Value.absent(),
    this.salePrice = const Value.absent(),
    this.costPrice = const Value.absent(),
    this.currency = const Value.absent(),
    this.description = const Value.absent(),
    this.level = const Value.absent(),
    this.hasPendingOp = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ProductsCompanion.insert({
    required String uuid,
    required String name,
    this.sku = const Value.absent(),
    this.barcode = const Value.absent(),
    this.categoryUuid = const Value.absent(),
    this.categoryName = const Value.absent(),
    this.quantity = const Value.absent(),
    this.alertThreshold = const Value.absent(),
    this.salePrice = const Value.absent(),
    this.costPrice = const Value.absent(),
    this.currency = const Value.absent(),
    this.description = const Value.absent(),
    this.level = const Value.absent(),
    this.hasPendingOp = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       name = Value(name);
  static Insertable<ProductRow> custom({
    Expression<String>? uuid,
    Expression<String>? name,
    Expression<String>? sku,
    Expression<String>? barcode,
    Expression<String>? categoryUuid,
    Expression<String>? categoryName,
    Expression<int>? quantity,
    Expression<int>? alertThreshold,
    Expression<String>? salePrice,
    Expression<String>? costPrice,
    Expression<String>? currency,
    Expression<String>? description,
    Expression<String>? level,
    Expression<bool>? hasPendingOp,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? deletedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (name != null) 'name': name,
      if (sku != null) 'sku': sku,
      if (barcode != null) 'barcode': barcode,
      if (categoryUuid != null) 'category_uuid': categoryUuid,
      if (categoryName != null) 'category_name': categoryName,
      if (quantity != null) 'quantity': quantity,
      if (alertThreshold != null) 'alert_threshold': alertThreshold,
      if (salePrice != null) 'sale_price': salePrice,
      if (costPrice != null) 'cost_price': costPrice,
      if (currency != null) 'currency': currency,
      if (description != null) 'description': description,
      if (level != null) 'level': level,
      if (hasPendingOp != null) 'has_pending_op': hasPendingOp,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (deletedAt != null) 'deleted_at': deletedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ProductsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? name,
    Value<String>? sku,
    Value<String>? barcode,
    Value<String?>? categoryUuid,
    Value<String>? categoryName,
    Value<int>? quantity,
    Value<int>? alertThreshold,
    Value<String>? salePrice,
    Value<String>? costPrice,
    Value<String>? currency,
    Value<String>? description,
    Value<String>? level,
    Value<bool>? hasPendingOp,
    Value<DateTime?>? updatedAt,
    Value<DateTime?>? deletedAt,
    Value<int>? rowid,
  }) {
    return ProductsCompanion(
      uuid: uuid ?? this.uuid,
      name: name ?? this.name,
      sku: sku ?? this.sku,
      barcode: barcode ?? this.barcode,
      categoryUuid: categoryUuid ?? this.categoryUuid,
      categoryName: categoryName ?? this.categoryName,
      quantity: quantity ?? this.quantity,
      alertThreshold: alertThreshold ?? this.alertThreshold,
      salePrice: salePrice ?? this.salePrice,
      costPrice: costPrice ?? this.costPrice,
      currency: currency ?? this.currency,
      description: description ?? this.description,
      level: level ?? this.level,
      hasPendingOp: hasPendingOp ?? this.hasPendingOp,
      updatedAt: updatedAt ?? this.updatedAt,
      deletedAt: deletedAt ?? this.deletedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (name.present) {
      map['name'] = Variable<String>(name.value);
    }
    if (sku.present) {
      map['sku'] = Variable<String>(sku.value);
    }
    if (barcode.present) {
      map['barcode'] = Variable<String>(barcode.value);
    }
    if (categoryUuid.present) {
      map['category_uuid'] = Variable<String>(categoryUuid.value);
    }
    if (categoryName.present) {
      map['category_name'] = Variable<String>(categoryName.value);
    }
    if (quantity.present) {
      map['quantity'] = Variable<int>(quantity.value);
    }
    if (alertThreshold.present) {
      map['alert_threshold'] = Variable<int>(alertThreshold.value);
    }
    if (salePrice.present) {
      map['sale_price'] = Variable<String>(salePrice.value);
    }
    if (costPrice.present) {
      map['cost_price'] = Variable<String>(costPrice.value);
    }
    if (currency.present) {
      map['currency'] = Variable<String>(currency.value);
    }
    if (description.present) {
      map['description'] = Variable<String>(description.value);
    }
    if (level.present) {
      map['level'] = Variable<String>(level.value);
    }
    if (hasPendingOp.present) {
      map['has_pending_op'] = Variable<bool>(hasPendingOp.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (deletedAt.present) {
      map['deleted_at'] = Variable<DateTime>(deletedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('ProductsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('name: $name, ')
          ..write('sku: $sku, ')
          ..write('barcode: $barcode, ')
          ..write('categoryUuid: $categoryUuid, ')
          ..write('categoryName: $categoryName, ')
          ..write('quantity: $quantity, ')
          ..write('alertThreshold: $alertThreshold, ')
          ..write('salePrice: $salePrice, ')
          ..write('costPrice: $costPrice, ')
          ..write('currency: $currency, ')
          ..write('description: $description, ')
          ..write('level: $level, ')
          ..write('hasPendingOp: $hasPendingOp, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $MovementsTable extends Movements
    with TableInfo<$MovementsTable, MovementRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $MovementsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _productUuidMeta = const VerificationMeta(
    'productUuid',
  );
  @override
  late final GeneratedColumn<String> productUuid = GeneratedColumn<String>(
    'product_uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _productNameMeta = const VerificationMeta(
    'productName',
  );
  @override
  late final GeneratedColumn<String> productName = GeneratedColumn<String>(
    'product_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _productSkuMeta = const VerificationMeta(
    'productSku',
  );
  @override
  late final GeneratedColumn<String> productSku = GeneratedColumn<String>(
    'product_sku',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _kindMeta = const VerificationMeta('kind');
  @override
  late final GeneratedColumn<String> kind = GeneratedColumn<String>(
    'kind',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _quantityMeta = const VerificationMeta(
    'quantity',
  );
  @override
  late final GeneratedColumn<int> quantity = GeneratedColumn<int>(
    'quantity',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _noteMeta = const VerificationMeta('note');
  @override
  late final GeneratedColumn<String> note = GeneratedColumn<String>(
    'note',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _usernameMeta = const VerificationMeta(
    'username',
  );
  @override
  late final GeneratedColumn<String> username = GeneratedColumn<String>(
    'username',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _hasPendingOpMeta = const VerificationMeta(
    'hasPendingOp',
  );
  @override
  late final GeneratedColumn<bool> hasPendingOp = GeneratedColumn<bool>(
    'has_pending_op',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("has_pending_op" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _deletedAtMeta = const VerificationMeta(
    'deletedAt',
  );
  @override
  late final GeneratedColumn<DateTime> deletedAt = GeneratedColumn<DateTime>(
    'deleted_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    productUuid,
    productName,
    productSku,
    kind,
    quantity,
    note,
    username,
    hasPendingOp,
    createdAt,
    updatedAt,
    deletedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'movements';
  @override
  VerificationContext validateIntegrity(
    Insertable<MovementRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('product_uuid')) {
      context.handle(
        _productUuidMeta,
        productUuid.isAcceptableOrUnknown(
          data['product_uuid']!,
          _productUuidMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_productUuidMeta);
    }
    if (data.containsKey('product_name')) {
      context.handle(
        _productNameMeta,
        productName.isAcceptableOrUnknown(
          data['product_name']!,
          _productNameMeta,
        ),
      );
    }
    if (data.containsKey('product_sku')) {
      context.handle(
        _productSkuMeta,
        productSku.isAcceptableOrUnknown(data['product_sku']!, _productSkuMeta),
      );
    }
    if (data.containsKey('kind')) {
      context.handle(
        _kindMeta,
        kind.isAcceptableOrUnknown(data['kind']!, _kindMeta),
      );
    } else if (isInserting) {
      context.missing(_kindMeta);
    }
    if (data.containsKey('quantity')) {
      context.handle(
        _quantityMeta,
        quantity.isAcceptableOrUnknown(data['quantity']!, _quantityMeta),
      );
    } else if (isInserting) {
      context.missing(_quantityMeta);
    }
    if (data.containsKey('note')) {
      context.handle(
        _noteMeta,
        note.isAcceptableOrUnknown(data['note']!, _noteMeta),
      );
    }
    if (data.containsKey('username')) {
      context.handle(
        _usernameMeta,
        username.isAcceptableOrUnknown(data['username']!, _usernameMeta),
      );
    }
    if (data.containsKey('has_pending_op')) {
      context.handle(
        _hasPendingOpMeta,
        hasPendingOp.isAcceptableOrUnknown(
          data['has_pending_op']!,
          _hasPendingOpMeta,
        ),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    if (data.containsKey('deleted_at')) {
      context.handle(
        _deletedAtMeta,
        deletedAt.isAcceptableOrUnknown(data['deleted_at']!, _deletedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  MovementRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return MovementRow(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      productUuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}product_uuid'],
      )!,
      productName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}product_name'],
      )!,
      productSku: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}product_sku'],
      )!,
      kind: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}kind'],
      )!,
      quantity: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}quantity'],
      )!,
      note: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}note'],
      )!,
      username: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}username'],
      )!,
      hasPendingOp: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}has_pending_op'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      ),
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      ),
      deletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}deleted_at'],
      ),
    );
  }

  @override
  $MovementsTable createAlias(String alias) {
    return $MovementsTable(attachedDatabase, alias);
  }
}

class MovementRow extends DataClass implements Insertable<MovementRow> {
  final String uuid;
  final String productUuid;
  final String productName;
  final String productSku;

  /// `IN`, `OUT` ou `ADJ`.
  final String kind;
  final int quantity;
  final String note;
  final String username;
  final bool hasPendingOp;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final DateTime? deletedAt;
  const MovementRow({
    required this.uuid,
    required this.productUuid,
    required this.productName,
    required this.productSku,
    required this.kind,
    required this.quantity,
    required this.note,
    required this.username,
    required this.hasPendingOp,
    this.createdAt,
    this.updatedAt,
    this.deletedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['product_uuid'] = Variable<String>(productUuid);
    map['product_name'] = Variable<String>(productName);
    map['product_sku'] = Variable<String>(productSku);
    map['kind'] = Variable<String>(kind);
    map['quantity'] = Variable<int>(quantity);
    map['note'] = Variable<String>(note);
    map['username'] = Variable<String>(username);
    map['has_pending_op'] = Variable<bool>(hasPendingOp);
    if (!nullToAbsent || createdAt != null) {
      map['created_at'] = Variable<DateTime>(createdAt);
    }
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    if (!nullToAbsent || deletedAt != null) {
      map['deleted_at'] = Variable<DateTime>(deletedAt);
    }
    return map;
  }

  MovementsCompanion toCompanion(bool nullToAbsent) {
    return MovementsCompanion(
      uuid: Value(uuid),
      productUuid: Value(productUuid),
      productName: Value(productName),
      productSku: Value(productSku),
      kind: Value(kind),
      quantity: Value(quantity),
      note: Value(note),
      username: Value(username),
      hasPendingOp: Value(hasPendingOp),
      createdAt: createdAt == null && nullToAbsent
          ? const Value.absent()
          : Value(createdAt),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
      deletedAt: deletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(deletedAt),
    );
  }

  factory MovementRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return MovementRow(
      uuid: serializer.fromJson<String>(json['uuid']),
      productUuid: serializer.fromJson<String>(json['productUuid']),
      productName: serializer.fromJson<String>(json['productName']),
      productSku: serializer.fromJson<String>(json['productSku']),
      kind: serializer.fromJson<String>(json['kind']),
      quantity: serializer.fromJson<int>(json['quantity']),
      note: serializer.fromJson<String>(json['note']),
      username: serializer.fromJson<String>(json['username']),
      hasPendingOp: serializer.fromJson<bool>(json['hasPendingOp']),
      createdAt: serializer.fromJson<DateTime?>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
      deletedAt: serializer.fromJson<DateTime?>(json['deletedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'productUuid': serializer.toJson<String>(productUuid),
      'productName': serializer.toJson<String>(productName),
      'productSku': serializer.toJson<String>(productSku),
      'kind': serializer.toJson<String>(kind),
      'quantity': serializer.toJson<int>(quantity),
      'note': serializer.toJson<String>(note),
      'username': serializer.toJson<String>(username),
      'hasPendingOp': serializer.toJson<bool>(hasPendingOp),
      'createdAt': serializer.toJson<DateTime?>(createdAt),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
      'deletedAt': serializer.toJson<DateTime?>(deletedAt),
    };
  }

  MovementRow copyWith({
    String? uuid,
    String? productUuid,
    String? productName,
    String? productSku,
    String? kind,
    int? quantity,
    String? note,
    String? username,
    bool? hasPendingOp,
    Value<DateTime?> createdAt = const Value.absent(),
    Value<DateTime?> updatedAt = const Value.absent(),
    Value<DateTime?> deletedAt = const Value.absent(),
  }) => MovementRow(
    uuid: uuid ?? this.uuid,
    productUuid: productUuid ?? this.productUuid,
    productName: productName ?? this.productName,
    productSku: productSku ?? this.productSku,
    kind: kind ?? this.kind,
    quantity: quantity ?? this.quantity,
    note: note ?? this.note,
    username: username ?? this.username,
    hasPendingOp: hasPendingOp ?? this.hasPendingOp,
    createdAt: createdAt.present ? createdAt.value : this.createdAt,
    updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
    deletedAt: deletedAt.present ? deletedAt.value : this.deletedAt,
  );
  MovementRow copyWithCompanion(MovementsCompanion data) {
    return MovementRow(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      productUuid: data.productUuid.present
          ? data.productUuid.value
          : this.productUuid,
      productName: data.productName.present
          ? data.productName.value
          : this.productName,
      productSku: data.productSku.present
          ? data.productSku.value
          : this.productSku,
      kind: data.kind.present ? data.kind.value : this.kind,
      quantity: data.quantity.present ? data.quantity.value : this.quantity,
      note: data.note.present ? data.note.value : this.note,
      username: data.username.present ? data.username.value : this.username,
      hasPendingOp: data.hasPendingOp.present
          ? data.hasPendingOp.value
          : this.hasPendingOp,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      deletedAt: data.deletedAt.present ? data.deletedAt.value : this.deletedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('MovementRow(')
          ..write('uuid: $uuid, ')
          ..write('productUuid: $productUuid, ')
          ..write('productName: $productName, ')
          ..write('productSku: $productSku, ')
          ..write('kind: $kind, ')
          ..write('quantity: $quantity, ')
          ..write('note: $note, ')
          ..write('username: $username, ')
          ..write('hasPendingOp: $hasPendingOp, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    productUuid,
    productName,
    productSku,
    kind,
    quantity,
    note,
    username,
    hasPendingOp,
    createdAt,
    updatedAt,
    deletedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is MovementRow &&
          other.uuid == this.uuid &&
          other.productUuid == this.productUuid &&
          other.productName == this.productName &&
          other.productSku == this.productSku &&
          other.kind == this.kind &&
          other.quantity == this.quantity &&
          other.note == this.note &&
          other.username == this.username &&
          other.hasPendingOp == this.hasPendingOp &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.deletedAt == this.deletedAt);
}

class MovementsCompanion extends UpdateCompanion<MovementRow> {
  final Value<String> uuid;
  final Value<String> productUuid;
  final Value<String> productName;
  final Value<String> productSku;
  final Value<String> kind;
  final Value<int> quantity;
  final Value<String> note;
  final Value<String> username;
  final Value<bool> hasPendingOp;
  final Value<DateTime?> createdAt;
  final Value<DateTime?> updatedAt;
  final Value<DateTime?> deletedAt;
  final Value<int> rowid;
  const MovementsCompanion({
    this.uuid = const Value.absent(),
    this.productUuid = const Value.absent(),
    this.productName = const Value.absent(),
    this.productSku = const Value.absent(),
    this.kind = const Value.absent(),
    this.quantity = const Value.absent(),
    this.note = const Value.absent(),
    this.username = const Value.absent(),
    this.hasPendingOp = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  MovementsCompanion.insert({
    required String uuid,
    required String productUuid,
    this.productName = const Value.absent(),
    this.productSku = const Value.absent(),
    required String kind,
    required int quantity,
    this.note = const Value.absent(),
    this.username = const Value.absent(),
    this.hasPendingOp = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       productUuid = Value(productUuid),
       kind = Value(kind),
       quantity = Value(quantity);
  static Insertable<MovementRow> custom({
    Expression<String>? uuid,
    Expression<String>? productUuid,
    Expression<String>? productName,
    Expression<String>? productSku,
    Expression<String>? kind,
    Expression<int>? quantity,
    Expression<String>? note,
    Expression<String>? username,
    Expression<bool>? hasPendingOp,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? deletedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (productUuid != null) 'product_uuid': productUuid,
      if (productName != null) 'product_name': productName,
      if (productSku != null) 'product_sku': productSku,
      if (kind != null) 'kind': kind,
      if (quantity != null) 'quantity': quantity,
      if (note != null) 'note': note,
      if (username != null) 'username': username,
      if (hasPendingOp != null) 'has_pending_op': hasPendingOp,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (deletedAt != null) 'deleted_at': deletedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  MovementsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? productUuid,
    Value<String>? productName,
    Value<String>? productSku,
    Value<String>? kind,
    Value<int>? quantity,
    Value<String>? note,
    Value<String>? username,
    Value<bool>? hasPendingOp,
    Value<DateTime?>? createdAt,
    Value<DateTime?>? updatedAt,
    Value<DateTime?>? deletedAt,
    Value<int>? rowid,
  }) {
    return MovementsCompanion(
      uuid: uuid ?? this.uuid,
      productUuid: productUuid ?? this.productUuid,
      productName: productName ?? this.productName,
      productSku: productSku ?? this.productSku,
      kind: kind ?? this.kind,
      quantity: quantity ?? this.quantity,
      note: note ?? this.note,
      username: username ?? this.username,
      hasPendingOp: hasPendingOp ?? this.hasPendingOp,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      deletedAt: deletedAt ?? this.deletedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (productUuid.present) {
      map['product_uuid'] = Variable<String>(productUuid.value);
    }
    if (productName.present) {
      map['product_name'] = Variable<String>(productName.value);
    }
    if (productSku.present) {
      map['product_sku'] = Variable<String>(productSku.value);
    }
    if (kind.present) {
      map['kind'] = Variable<String>(kind.value);
    }
    if (quantity.present) {
      map['quantity'] = Variable<int>(quantity.value);
    }
    if (note.present) {
      map['note'] = Variable<String>(note.value);
    }
    if (username.present) {
      map['username'] = Variable<String>(username.value);
    }
    if (hasPendingOp.present) {
      map['has_pending_op'] = Variable<bool>(hasPendingOp.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (deletedAt.present) {
      map['deleted_at'] = Variable<DateTime>(deletedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('MovementsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('productUuid: $productUuid, ')
          ..write('productName: $productName, ')
          ..write('productSku: $productSku, ')
          ..write('kind: $kind, ')
          ..write('quantity: $quantity, ')
          ..write('note: $note, ')
          ..write('username: $username, ')
          ..write('hasPendingOp: $hasPendingOp, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $NotificationsTable extends Notifications
    with TableInfo<$NotificationsTable, NotificationRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $NotificationsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _kindMeta = const VerificationMeta('kind');
  @override
  late final GeneratedColumn<String> kind = GeneratedColumn<String>(
    'kind',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _kindLabelMeta = const VerificationMeta(
    'kindLabel',
  );
  @override
  late final GeneratedColumn<String> kindLabel = GeneratedColumn<String>(
    'kind_label',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _messageMeta = const VerificationMeta(
    'message',
  );
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>(
    'message',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _productNameMeta = const VerificationMeta(
    'productName',
  );
  @override
  late final GeneratedColumn<String> productName = GeneratedColumn<String>(
    'product_name',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _quantityMeta = const VerificationMeta(
    'quantity',
  );
  @override
  late final GeneratedColumn<int> quantity = GeneratedColumn<int>(
    'quantity',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _alertThresholdMeta = const VerificationMeta(
    'alertThreshold',
  );
  @override
  late final GeneratedColumn<int> alertThreshold = GeneratedColumn<int>(
    'alert_threshold',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _levelMeta = const VerificationMeta('level');
  @override
  late final GeneratedColumn<String> level = GeneratedColumn<String>(
    'level',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _toneMeta = const VerificationMeta('tone');
  @override
  late final GeneratedColumn<int> tone = GeneratedColumn<int>(
    'tone',
    aliasedName,
    true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _isReadMeta = const VerificationMeta('isRead');
  @override
  late final GeneratedColumn<bool> isRead = GeneratedColumn<bool>(
    'is_read',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("is_read" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _hasPendingOpMeta = const VerificationMeta(
    'hasPendingOp',
  );
  @override
  late final GeneratedColumn<bool> hasPendingOp = GeneratedColumn<bool>(
    'has_pending_op',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("has_pending_op" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _deletedAtMeta = const VerificationMeta(
    'deletedAt',
  );
  @override
  late final GeneratedColumn<DateTime> deletedAt = GeneratedColumn<DateTime>(
    'deleted_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    kind,
    kindLabel,
    message,
    productName,
    quantity,
    alertThreshold,
    level,
    tone,
    isRead,
    hasPendingOp,
    createdAt,
    updatedAt,
    deletedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'notifications';
  @override
  VerificationContext validateIntegrity(
    Insertable<NotificationRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('kind')) {
      context.handle(
        _kindMeta,
        kind.isAcceptableOrUnknown(data['kind']!, _kindMeta),
      );
    }
    if (data.containsKey('kind_label')) {
      context.handle(
        _kindLabelMeta,
        kindLabel.isAcceptableOrUnknown(data['kind_label']!, _kindLabelMeta),
      );
    }
    if (data.containsKey('message')) {
      context.handle(
        _messageMeta,
        message.isAcceptableOrUnknown(data['message']!, _messageMeta),
      );
    }
    if (data.containsKey('product_name')) {
      context.handle(
        _productNameMeta,
        productName.isAcceptableOrUnknown(
          data['product_name']!,
          _productNameMeta,
        ),
      );
    }
    if (data.containsKey('quantity')) {
      context.handle(
        _quantityMeta,
        quantity.isAcceptableOrUnknown(data['quantity']!, _quantityMeta),
      );
    }
    if (data.containsKey('alert_threshold')) {
      context.handle(
        _alertThresholdMeta,
        alertThreshold.isAcceptableOrUnknown(
          data['alert_threshold']!,
          _alertThresholdMeta,
        ),
      );
    }
    if (data.containsKey('level')) {
      context.handle(
        _levelMeta,
        level.isAcceptableOrUnknown(data['level']!, _levelMeta),
      );
    }
    if (data.containsKey('tone')) {
      context.handle(
        _toneMeta,
        tone.isAcceptableOrUnknown(data['tone']!, _toneMeta),
      );
    }
    if (data.containsKey('is_read')) {
      context.handle(
        _isReadMeta,
        isRead.isAcceptableOrUnknown(data['is_read']!, _isReadMeta),
      );
    }
    if (data.containsKey('has_pending_op')) {
      context.handle(
        _hasPendingOpMeta,
        hasPendingOp.isAcceptableOrUnknown(
          data['has_pending_op']!,
          _hasPendingOpMeta,
        ),
      );
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    if (data.containsKey('deleted_at')) {
      context.handle(
        _deletedAtMeta,
        deletedAt.isAcceptableOrUnknown(data['deleted_at']!, _deletedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  NotificationRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return NotificationRow(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      kind: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}kind'],
      )!,
      kindLabel: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}kind_label'],
      )!,
      message: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}message'],
      )!,
      productName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}product_name'],
      ),
      quantity: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}quantity'],
      ),
      alertThreshold: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}alert_threshold'],
      ),
      level: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}level'],
      ),
      tone: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}tone'],
      ),
      isRead: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}is_read'],
      )!,
      hasPendingOp: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}has_pending_op'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      ),
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      ),
      deletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}deleted_at'],
      ),
    );
  }

  @override
  $NotificationsTable createAlias(String alias) {
    return $NotificationsTable(attachedDatabase, alias);
  }
}

class NotificationRow extends DataClass implements Insertable<NotificationRow> {
  final String uuid;
  final String kind;
  final String kindLabel;
  final String message;
  final String? productName;
  final int? quantity;
  final int? alertThreshold;
  final String? level;
  final int? tone;
  final bool isRead;
  final bool hasPendingOp;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final DateTime? deletedAt;
  const NotificationRow({
    required this.uuid,
    required this.kind,
    required this.kindLabel,
    required this.message,
    this.productName,
    this.quantity,
    this.alertThreshold,
    this.level,
    this.tone,
    required this.isRead,
    required this.hasPendingOp,
    this.createdAt,
    this.updatedAt,
    this.deletedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['kind'] = Variable<String>(kind);
    map['kind_label'] = Variable<String>(kindLabel);
    map['message'] = Variable<String>(message);
    if (!nullToAbsent || productName != null) {
      map['product_name'] = Variable<String>(productName);
    }
    if (!nullToAbsent || quantity != null) {
      map['quantity'] = Variable<int>(quantity);
    }
    if (!nullToAbsent || alertThreshold != null) {
      map['alert_threshold'] = Variable<int>(alertThreshold);
    }
    if (!nullToAbsent || level != null) {
      map['level'] = Variable<String>(level);
    }
    if (!nullToAbsent || tone != null) {
      map['tone'] = Variable<int>(tone);
    }
    map['is_read'] = Variable<bool>(isRead);
    map['has_pending_op'] = Variable<bool>(hasPendingOp);
    if (!nullToAbsent || createdAt != null) {
      map['created_at'] = Variable<DateTime>(createdAt);
    }
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    if (!nullToAbsent || deletedAt != null) {
      map['deleted_at'] = Variable<DateTime>(deletedAt);
    }
    return map;
  }

  NotificationsCompanion toCompanion(bool nullToAbsent) {
    return NotificationsCompanion(
      uuid: Value(uuid),
      kind: Value(kind),
      kindLabel: Value(kindLabel),
      message: Value(message),
      productName: productName == null && nullToAbsent
          ? const Value.absent()
          : Value(productName),
      quantity: quantity == null && nullToAbsent
          ? const Value.absent()
          : Value(quantity),
      alertThreshold: alertThreshold == null && nullToAbsent
          ? const Value.absent()
          : Value(alertThreshold),
      level: level == null && nullToAbsent
          ? const Value.absent()
          : Value(level),
      tone: tone == null && nullToAbsent ? const Value.absent() : Value(tone),
      isRead: Value(isRead),
      hasPendingOp: Value(hasPendingOp),
      createdAt: createdAt == null && nullToAbsent
          ? const Value.absent()
          : Value(createdAt),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
      deletedAt: deletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(deletedAt),
    );
  }

  factory NotificationRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return NotificationRow(
      uuid: serializer.fromJson<String>(json['uuid']),
      kind: serializer.fromJson<String>(json['kind']),
      kindLabel: serializer.fromJson<String>(json['kindLabel']),
      message: serializer.fromJson<String>(json['message']),
      productName: serializer.fromJson<String?>(json['productName']),
      quantity: serializer.fromJson<int?>(json['quantity']),
      alertThreshold: serializer.fromJson<int?>(json['alertThreshold']),
      level: serializer.fromJson<String?>(json['level']),
      tone: serializer.fromJson<int?>(json['tone']),
      isRead: serializer.fromJson<bool>(json['isRead']),
      hasPendingOp: serializer.fromJson<bool>(json['hasPendingOp']),
      createdAt: serializer.fromJson<DateTime?>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
      deletedAt: serializer.fromJson<DateTime?>(json['deletedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'kind': serializer.toJson<String>(kind),
      'kindLabel': serializer.toJson<String>(kindLabel),
      'message': serializer.toJson<String>(message),
      'productName': serializer.toJson<String?>(productName),
      'quantity': serializer.toJson<int?>(quantity),
      'alertThreshold': serializer.toJson<int?>(alertThreshold),
      'level': serializer.toJson<String?>(level),
      'tone': serializer.toJson<int?>(tone),
      'isRead': serializer.toJson<bool>(isRead),
      'hasPendingOp': serializer.toJson<bool>(hasPendingOp),
      'createdAt': serializer.toJson<DateTime?>(createdAt),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
      'deletedAt': serializer.toJson<DateTime?>(deletedAt),
    };
  }

  NotificationRow copyWith({
    String? uuid,
    String? kind,
    String? kindLabel,
    String? message,
    Value<String?> productName = const Value.absent(),
    Value<int?> quantity = const Value.absent(),
    Value<int?> alertThreshold = const Value.absent(),
    Value<String?> level = const Value.absent(),
    Value<int?> tone = const Value.absent(),
    bool? isRead,
    bool? hasPendingOp,
    Value<DateTime?> createdAt = const Value.absent(),
    Value<DateTime?> updatedAt = const Value.absent(),
    Value<DateTime?> deletedAt = const Value.absent(),
  }) => NotificationRow(
    uuid: uuid ?? this.uuid,
    kind: kind ?? this.kind,
    kindLabel: kindLabel ?? this.kindLabel,
    message: message ?? this.message,
    productName: productName.present ? productName.value : this.productName,
    quantity: quantity.present ? quantity.value : this.quantity,
    alertThreshold: alertThreshold.present
        ? alertThreshold.value
        : this.alertThreshold,
    level: level.present ? level.value : this.level,
    tone: tone.present ? tone.value : this.tone,
    isRead: isRead ?? this.isRead,
    hasPendingOp: hasPendingOp ?? this.hasPendingOp,
    createdAt: createdAt.present ? createdAt.value : this.createdAt,
    updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
    deletedAt: deletedAt.present ? deletedAt.value : this.deletedAt,
  );
  NotificationRow copyWithCompanion(NotificationsCompanion data) {
    return NotificationRow(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      kind: data.kind.present ? data.kind.value : this.kind,
      kindLabel: data.kindLabel.present ? data.kindLabel.value : this.kindLabel,
      message: data.message.present ? data.message.value : this.message,
      productName: data.productName.present
          ? data.productName.value
          : this.productName,
      quantity: data.quantity.present ? data.quantity.value : this.quantity,
      alertThreshold: data.alertThreshold.present
          ? data.alertThreshold.value
          : this.alertThreshold,
      level: data.level.present ? data.level.value : this.level,
      tone: data.tone.present ? data.tone.value : this.tone,
      isRead: data.isRead.present ? data.isRead.value : this.isRead,
      hasPendingOp: data.hasPendingOp.present
          ? data.hasPendingOp.value
          : this.hasPendingOp,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      deletedAt: data.deletedAt.present ? data.deletedAt.value : this.deletedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('NotificationRow(')
          ..write('uuid: $uuid, ')
          ..write('kind: $kind, ')
          ..write('kindLabel: $kindLabel, ')
          ..write('message: $message, ')
          ..write('productName: $productName, ')
          ..write('quantity: $quantity, ')
          ..write('alertThreshold: $alertThreshold, ')
          ..write('level: $level, ')
          ..write('tone: $tone, ')
          ..write('isRead: $isRead, ')
          ..write('hasPendingOp: $hasPendingOp, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    kind,
    kindLabel,
    message,
    productName,
    quantity,
    alertThreshold,
    level,
    tone,
    isRead,
    hasPendingOp,
    createdAt,
    updatedAt,
    deletedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is NotificationRow &&
          other.uuid == this.uuid &&
          other.kind == this.kind &&
          other.kindLabel == this.kindLabel &&
          other.message == this.message &&
          other.productName == this.productName &&
          other.quantity == this.quantity &&
          other.alertThreshold == this.alertThreshold &&
          other.level == this.level &&
          other.tone == this.tone &&
          other.isRead == this.isRead &&
          other.hasPendingOp == this.hasPendingOp &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt &&
          other.deletedAt == this.deletedAt);
}

class NotificationsCompanion extends UpdateCompanion<NotificationRow> {
  final Value<String> uuid;
  final Value<String> kind;
  final Value<String> kindLabel;
  final Value<String> message;
  final Value<String?> productName;
  final Value<int?> quantity;
  final Value<int?> alertThreshold;
  final Value<String?> level;
  final Value<int?> tone;
  final Value<bool> isRead;
  final Value<bool> hasPendingOp;
  final Value<DateTime?> createdAt;
  final Value<DateTime?> updatedAt;
  final Value<DateTime?> deletedAt;
  final Value<int> rowid;
  const NotificationsCompanion({
    this.uuid = const Value.absent(),
    this.kind = const Value.absent(),
    this.kindLabel = const Value.absent(),
    this.message = const Value.absent(),
    this.productName = const Value.absent(),
    this.quantity = const Value.absent(),
    this.alertThreshold = const Value.absent(),
    this.level = const Value.absent(),
    this.tone = const Value.absent(),
    this.isRead = const Value.absent(),
    this.hasPendingOp = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  NotificationsCompanion.insert({
    required String uuid,
    this.kind = const Value.absent(),
    this.kindLabel = const Value.absent(),
    this.message = const Value.absent(),
    this.productName = const Value.absent(),
    this.quantity = const Value.absent(),
    this.alertThreshold = const Value.absent(),
    this.level = const Value.absent(),
    this.tone = const Value.absent(),
    this.isRead = const Value.absent(),
    this.hasPendingOp = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid);
  static Insertable<NotificationRow> custom({
    Expression<String>? uuid,
    Expression<String>? kind,
    Expression<String>? kindLabel,
    Expression<String>? message,
    Expression<String>? productName,
    Expression<int>? quantity,
    Expression<int>? alertThreshold,
    Expression<String>? level,
    Expression<int>? tone,
    Expression<bool>? isRead,
    Expression<bool>? hasPendingOp,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? deletedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (kind != null) 'kind': kind,
      if (kindLabel != null) 'kind_label': kindLabel,
      if (message != null) 'message': message,
      if (productName != null) 'product_name': productName,
      if (quantity != null) 'quantity': quantity,
      if (alertThreshold != null) 'alert_threshold': alertThreshold,
      if (level != null) 'level': level,
      if (tone != null) 'tone': tone,
      if (isRead != null) 'is_read': isRead,
      if (hasPendingOp != null) 'has_pending_op': hasPendingOp,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (deletedAt != null) 'deleted_at': deletedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  NotificationsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? kind,
    Value<String>? kindLabel,
    Value<String>? message,
    Value<String?>? productName,
    Value<int?>? quantity,
    Value<int?>? alertThreshold,
    Value<String?>? level,
    Value<int?>? tone,
    Value<bool>? isRead,
    Value<bool>? hasPendingOp,
    Value<DateTime?>? createdAt,
    Value<DateTime?>? updatedAt,
    Value<DateTime?>? deletedAt,
    Value<int>? rowid,
  }) {
    return NotificationsCompanion(
      uuid: uuid ?? this.uuid,
      kind: kind ?? this.kind,
      kindLabel: kindLabel ?? this.kindLabel,
      message: message ?? this.message,
      productName: productName ?? this.productName,
      quantity: quantity ?? this.quantity,
      alertThreshold: alertThreshold ?? this.alertThreshold,
      level: level ?? this.level,
      tone: tone ?? this.tone,
      isRead: isRead ?? this.isRead,
      hasPendingOp: hasPendingOp ?? this.hasPendingOp,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      deletedAt: deletedAt ?? this.deletedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (kind.present) {
      map['kind'] = Variable<String>(kind.value);
    }
    if (kindLabel.present) {
      map['kind_label'] = Variable<String>(kindLabel.value);
    }
    if (message.present) {
      map['message'] = Variable<String>(message.value);
    }
    if (productName.present) {
      map['product_name'] = Variable<String>(productName.value);
    }
    if (quantity.present) {
      map['quantity'] = Variable<int>(quantity.value);
    }
    if (alertThreshold.present) {
      map['alert_threshold'] = Variable<int>(alertThreshold.value);
    }
    if (level.present) {
      map['level'] = Variable<String>(level.value);
    }
    if (tone.present) {
      map['tone'] = Variable<int>(tone.value);
    }
    if (isRead.present) {
      map['is_read'] = Variable<bool>(isRead.value);
    }
    if (hasPendingOp.present) {
      map['has_pending_op'] = Variable<bool>(hasPendingOp.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (deletedAt.present) {
      map['deleted_at'] = Variable<DateTime>(deletedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('NotificationsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('kind: $kind, ')
          ..write('kindLabel: $kindLabel, ')
          ..write('message: $message, ')
          ..write('productName: $productName, ')
          ..write('quantity: $quantity, ')
          ..write('alertThreshold: $alertThreshold, ')
          ..write('level: $level, ')
          ..write('tone: $tone, ')
          ..write('isRead: $isRead, ')
          ..write('hasPendingOp: $hasPendingOp, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $MembershipsTable extends Memberships
    with TableInfo<$MembershipsTable, MembershipRow> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $MembershipsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _uuidMeta = const VerificationMeta('uuid');
  @override
  late final GeneratedColumn<String> uuid = GeneratedColumn<String>(
    'uuid',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _usernameMeta = const VerificationMeta(
    'username',
  );
  @override
  late final GeneratedColumn<String> username = GeneratedColumn<String>(
    'username',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _fullNameMeta = const VerificationMeta(
    'fullName',
  );
  @override
  late final GeneratedColumn<String> fullName = GeneratedColumn<String>(
    'full_name',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _roleMeta = const VerificationMeta('role');
  @override
  late final GeneratedColumn<String> role = GeneratedColumn<String>(
    'role',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant(''),
  );
  static const VerificationMeta _isOwnerMeta = const VerificationMeta(
    'isOwner',
  );
  @override
  late final GeneratedColumn<bool> isOwner = GeneratedColumn<bool>(
    'is_owner',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("is_owner" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _canViewProductsMeta = const VerificationMeta(
    'canViewProducts',
  );
  @override
  late final GeneratedColumn<bool> canViewProducts = GeneratedColumn<bool>(
    'can_view_products',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_view_products" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _canAddProductsMeta = const VerificationMeta(
    'canAddProducts',
  );
  @override
  late final GeneratedColumn<bool> canAddProducts = GeneratedColumn<bool>(
    'can_add_products',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_add_products" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _canEditProductsMeta = const VerificationMeta(
    'canEditProducts',
  );
  @override
  late final GeneratedColumn<bool> canEditProducts = GeneratedColumn<bool>(
    'can_edit_products',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_edit_products" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _canDeleteProductsMeta = const VerificationMeta(
    'canDeleteProducts',
  );
  @override
  late final GeneratedColumn<bool> canDeleteProducts = GeneratedColumn<bool>(
    'can_delete_products',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_delete_products" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _canManageStockMeta = const VerificationMeta(
    'canManageStock',
  );
  @override
  late final GeneratedColumn<bool> canManageStock = GeneratedColumn<bool>(
    'can_manage_stock',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_manage_stock" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _canManageCategoriesMeta =
      const VerificationMeta('canManageCategories');
  @override
  late final GeneratedColumn<bool> canManageCategories = GeneratedColumn<bool>(
    'can_manage_categories',
    aliasedName,
    false,
    type: DriftSqlType.bool,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'CHECK ("can_manage_categories" IN (0, 1))',
    ),
    defaultValue: const Constant(false),
  );
  static const VerificationMeta _updatedAtMeta = const VerificationMeta(
    'updatedAt',
  );
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
    'updated_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _deletedAtMeta = const VerificationMeta(
    'deletedAt',
  );
  @override
  late final GeneratedColumn<DateTime> deletedAt = GeneratedColumn<DateTime>(
    'deleted_at',
    aliasedName,
    true,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    uuid,
    username,
    fullName,
    role,
    isOwner,
    canViewProducts,
    canAddProducts,
    canEditProducts,
    canDeleteProducts,
    canManageStock,
    canManageCategories,
    updatedAt,
    deletedAt,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'memberships';
  @override
  VerificationContext validateIntegrity(
    Insertable<MembershipRow> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('uuid')) {
      context.handle(
        _uuidMeta,
        uuid.isAcceptableOrUnknown(data['uuid']!, _uuidMeta),
      );
    } else if (isInserting) {
      context.missing(_uuidMeta);
    }
    if (data.containsKey('username')) {
      context.handle(
        _usernameMeta,
        username.isAcceptableOrUnknown(data['username']!, _usernameMeta),
      );
    } else if (isInserting) {
      context.missing(_usernameMeta);
    }
    if (data.containsKey('full_name')) {
      context.handle(
        _fullNameMeta,
        fullName.isAcceptableOrUnknown(data['full_name']!, _fullNameMeta),
      );
    }
    if (data.containsKey('role')) {
      context.handle(
        _roleMeta,
        role.isAcceptableOrUnknown(data['role']!, _roleMeta),
      );
    }
    if (data.containsKey('is_owner')) {
      context.handle(
        _isOwnerMeta,
        isOwner.isAcceptableOrUnknown(data['is_owner']!, _isOwnerMeta),
      );
    }
    if (data.containsKey('can_view_products')) {
      context.handle(
        _canViewProductsMeta,
        canViewProducts.isAcceptableOrUnknown(
          data['can_view_products']!,
          _canViewProductsMeta,
        ),
      );
    }
    if (data.containsKey('can_add_products')) {
      context.handle(
        _canAddProductsMeta,
        canAddProducts.isAcceptableOrUnknown(
          data['can_add_products']!,
          _canAddProductsMeta,
        ),
      );
    }
    if (data.containsKey('can_edit_products')) {
      context.handle(
        _canEditProductsMeta,
        canEditProducts.isAcceptableOrUnknown(
          data['can_edit_products']!,
          _canEditProductsMeta,
        ),
      );
    }
    if (data.containsKey('can_delete_products')) {
      context.handle(
        _canDeleteProductsMeta,
        canDeleteProducts.isAcceptableOrUnknown(
          data['can_delete_products']!,
          _canDeleteProductsMeta,
        ),
      );
    }
    if (data.containsKey('can_manage_stock')) {
      context.handle(
        _canManageStockMeta,
        canManageStock.isAcceptableOrUnknown(
          data['can_manage_stock']!,
          _canManageStockMeta,
        ),
      );
    }
    if (data.containsKey('can_manage_categories')) {
      context.handle(
        _canManageCategoriesMeta,
        canManageCategories.isAcceptableOrUnknown(
          data['can_manage_categories']!,
          _canManageCategoriesMeta,
        ),
      );
    }
    if (data.containsKey('updated_at')) {
      context.handle(
        _updatedAtMeta,
        updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta),
      );
    }
    if (data.containsKey('deleted_at')) {
      context.handle(
        _deletedAtMeta,
        deletedAt.isAcceptableOrUnknown(data['deleted_at']!, _deletedAtMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {uuid};
  @override
  MembershipRow map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return MembershipRow(
      uuid: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}uuid'],
      )!,
      username: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}username'],
      )!,
      fullName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}full_name'],
      )!,
      role: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}role'],
      )!,
      isOwner: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}is_owner'],
      )!,
      canViewProducts: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_view_products'],
      )!,
      canAddProducts: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_add_products'],
      )!,
      canEditProducts: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_edit_products'],
      )!,
      canDeleteProducts: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_delete_products'],
      )!,
      canManageStock: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_manage_stock'],
      )!,
      canManageCategories: attachedDatabase.typeMapping.read(
        DriftSqlType.bool,
        data['${effectivePrefix}can_manage_categories'],
      )!,
      updatedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}updated_at'],
      ),
      deletedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}deleted_at'],
      ),
    );
  }

  @override
  $MembershipsTable createAlias(String alias) {
    return $MembershipsTable(attachedDatabase, alias);
  }
}

class MembershipRow extends DataClass implements Insertable<MembershipRow> {
  final String uuid;
  final String username;
  final String fullName;
  final String role;
  final bool isOwner;

  /// Drapeaux bruts : `Membership.has()` accorde tout au propriétaire, donc
  /// un écran qui lit ces colonnes doit passer par `hasPermission`.
  final bool canViewProducts;
  final bool canAddProducts;
  final bool canEditProducts;
  final bool canDeleteProducts;
  final bool canManageStock;
  final bool canManageCategories;
  final DateTime? updatedAt;
  final DateTime? deletedAt;
  const MembershipRow({
    required this.uuid,
    required this.username,
    required this.fullName,
    required this.role,
    required this.isOwner,
    required this.canViewProducts,
    required this.canAddProducts,
    required this.canEditProducts,
    required this.canDeleteProducts,
    required this.canManageStock,
    required this.canManageCategories,
    this.updatedAt,
    this.deletedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['uuid'] = Variable<String>(uuid);
    map['username'] = Variable<String>(username);
    map['full_name'] = Variable<String>(fullName);
    map['role'] = Variable<String>(role);
    map['is_owner'] = Variable<bool>(isOwner);
    map['can_view_products'] = Variable<bool>(canViewProducts);
    map['can_add_products'] = Variable<bool>(canAddProducts);
    map['can_edit_products'] = Variable<bool>(canEditProducts);
    map['can_delete_products'] = Variable<bool>(canDeleteProducts);
    map['can_manage_stock'] = Variable<bool>(canManageStock);
    map['can_manage_categories'] = Variable<bool>(canManageCategories);
    if (!nullToAbsent || updatedAt != null) {
      map['updated_at'] = Variable<DateTime>(updatedAt);
    }
    if (!nullToAbsent || deletedAt != null) {
      map['deleted_at'] = Variable<DateTime>(deletedAt);
    }
    return map;
  }

  MembershipsCompanion toCompanion(bool nullToAbsent) {
    return MembershipsCompanion(
      uuid: Value(uuid),
      username: Value(username),
      fullName: Value(fullName),
      role: Value(role),
      isOwner: Value(isOwner),
      canViewProducts: Value(canViewProducts),
      canAddProducts: Value(canAddProducts),
      canEditProducts: Value(canEditProducts),
      canDeleteProducts: Value(canDeleteProducts),
      canManageStock: Value(canManageStock),
      canManageCategories: Value(canManageCategories),
      updatedAt: updatedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(updatedAt),
      deletedAt: deletedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(deletedAt),
    );
  }

  factory MembershipRow.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return MembershipRow(
      uuid: serializer.fromJson<String>(json['uuid']),
      username: serializer.fromJson<String>(json['username']),
      fullName: serializer.fromJson<String>(json['fullName']),
      role: serializer.fromJson<String>(json['role']),
      isOwner: serializer.fromJson<bool>(json['isOwner']),
      canViewProducts: serializer.fromJson<bool>(json['canViewProducts']),
      canAddProducts: serializer.fromJson<bool>(json['canAddProducts']),
      canEditProducts: serializer.fromJson<bool>(json['canEditProducts']),
      canDeleteProducts: serializer.fromJson<bool>(json['canDeleteProducts']),
      canManageStock: serializer.fromJson<bool>(json['canManageStock']),
      canManageCategories: serializer.fromJson<bool>(
        json['canManageCategories'],
      ),
      updatedAt: serializer.fromJson<DateTime?>(json['updatedAt']),
      deletedAt: serializer.fromJson<DateTime?>(json['deletedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'uuid': serializer.toJson<String>(uuid),
      'username': serializer.toJson<String>(username),
      'fullName': serializer.toJson<String>(fullName),
      'role': serializer.toJson<String>(role),
      'isOwner': serializer.toJson<bool>(isOwner),
      'canViewProducts': serializer.toJson<bool>(canViewProducts),
      'canAddProducts': serializer.toJson<bool>(canAddProducts),
      'canEditProducts': serializer.toJson<bool>(canEditProducts),
      'canDeleteProducts': serializer.toJson<bool>(canDeleteProducts),
      'canManageStock': serializer.toJson<bool>(canManageStock),
      'canManageCategories': serializer.toJson<bool>(canManageCategories),
      'updatedAt': serializer.toJson<DateTime?>(updatedAt),
      'deletedAt': serializer.toJson<DateTime?>(deletedAt),
    };
  }

  MembershipRow copyWith({
    String? uuid,
    String? username,
    String? fullName,
    String? role,
    bool? isOwner,
    bool? canViewProducts,
    bool? canAddProducts,
    bool? canEditProducts,
    bool? canDeleteProducts,
    bool? canManageStock,
    bool? canManageCategories,
    Value<DateTime?> updatedAt = const Value.absent(),
    Value<DateTime?> deletedAt = const Value.absent(),
  }) => MembershipRow(
    uuid: uuid ?? this.uuid,
    username: username ?? this.username,
    fullName: fullName ?? this.fullName,
    role: role ?? this.role,
    isOwner: isOwner ?? this.isOwner,
    canViewProducts: canViewProducts ?? this.canViewProducts,
    canAddProducts: canAddProducts ?? this.canAddProducts,
    canEditProducts: canEditProducts ?? this.canEditProducts,
    canDeleteProducts: canDeleteProducts ?? this.canDeleteProducts,
    canManageStock: canManageStock ?? this.canManageStock,
    canManageCategories: canManageCategories ?? this.canManageCategories,
    updatedAt: updatedAt.present ? updatedAt.value : this.updatedAt,
    deletedAt: deletedAt.present ? deletedAt.value : this.deletedAt,
  );
  MembershipRow copyWithCompanion(MembershipsCompanion data) {
    return MembershipRow(
      uuid: data.uuid.present ? data.uuid.value : this.uuid,
      username: data.username.present ? data.username.value : this.username,
      fullName: data.fullName.present ? data.fullName.value : this.fullName,
      role: data.role.present ? data.role.value : this.role,
      isOwner: data.isOwner.present ? data.isOwner.value : this.isOwner,
      canViewProducts: data.canViewProducts.present
          ? data.canViewProducts.value
          : this.canViewProducts,
      canAddProducts: data.canAddProducts.present
          ? data.canAddProducts.value
          : this.canAddProducts,
      canEditProducts: data.canEditProducts.present
          ? data.canEditProducts.value
          : this.canEditProducts,
      canDeleteProducts: data.canDeleteProducts.present
          ? data.canDeleteProducts.value
          : this.canDeleteProducts,
      canManageStock: data.canManageStock.present
          ? data.canManageStock.value
          : this.canManageStock,
      canManageCategories: data.canManageCategories.present
          ? data.canManageCategories.value
          : this.canManageCategories,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
      deletedAt: data.deletedAt.present ? data.deletedAt.value : this.deletedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('MembershipRow(')
          ..write('uuid: $uuid, ')
          ..write('username: $username, ')
          ..write('fullName: $fullName, ')
          ..write('role: $role, ')
          ..write('isOwner: $isOwner, ')
          ..write('canViewProducts: $canViewProducts, ')
          ..write('canAddProducts: $canAddProducts, ')
          ..write('canEditProducts: $canEditProducts, ')
          ..write('canDeleteProducts: $canDeleteProducts, ')
          ..write('canManageStock: $canManageStock, ')
          ..write('canManageCategories: $canManageCategories, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    uuid,
    username,
    fullName,
    role,
    isOwner,
    canViewProducts,
    canAddProducts,
    canEditProducts,
    canDeleteProducts,
    canManageStock,
    canManageCategories,
    updatedAt,
    deletedAt,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is MembershipRow &&
          other.uuid == this.uuid &&
          other.username == this.username &&
          other.fullName == this.fullName &&
          other.role == this.role &&
          other.isOwner == this.isOwner &&
          other.canViewProducts == this.canViewProducts &&
          other.canAddProducts == this.canAddProducts &&
          other.canEditProducts == this.canEditProducts &&
          other.canDeleteProducts == this.canDeleteProducts &&
          other.canManageStock == this.canManageStock &&
          other.canManageCategories == this.canManageCategories &&
          other.updatedAt == this.updatedAt &&
          other.deletedAt == this.deletedAt);
}

class MembershipsCompanion extends UpdateCompanion<MembershipRow> {
  final Value<String> uuid;
  final Value<String> username;
  final Value<String> fullName;
  final Value<String> role;
  final Value<bool> isOwner;
  final Value<bool> canViewProducts;
  final Value<bool> canAddProducts;
  final Value<bool> canEditProducts;
  final Value<bool> canDeleteProducts;
  final Value<bool> canManageStock;
  final Value<bool> canManageCategories;
  final Value<DateTime?> updatedAt;
  final Value<DateTime?> deletedAt;
  final Value<int> rowid;
  const MembershipsCompanion({
    this.uuid = const Value.absent(),
    this.username = const Value.absent(),
    this.fullName = const Value.absent(),
    this.role = const Value.absent(),
    this.isOwner = const Value.absent(),
    this.canViewProducts = const Value.absent(),
    this.canAddProducts = const Value.absent(),
    this.canEditProducts = const Value.absent(),
    this.canDeleteProducts = const Value.absent(),
    this.canManageStock = const Value.absent(),
    this.canManageCategories = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  MembershipsCompanion.insert({
    required String uuid,
    required String username,
    this.fullName = const Value.absent(),
    this.role = const Value.absent(),
    this.isOwner = const Value.absent(),
    this.canViewProducts = const Value.absent(),
    this.canAddProducts = const Value.absent(),
    this.canEditProducts = const Value.absent(),
    this.canDeleteProducts = const Value.absent(),
    this.canManageStock = const Value.absent(),
    this.canManageCategories = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.deletedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : uuid = Value(uuid),
       username = Value(username);
  static Insertable<MembershipRow> custom({
    Expression<String>? uuid,
    Expression<String>? username,
    Expression<String>? fullName,
    Expression<String>? role,
    Expression<bool>? isOwner,
    Expression<bool>? canViewProducts,
    Expression<bool>? canAddProducts,
    Expression<bool>? canEditProducts,
    Expression<bool>? canDeleteProducts,
    Expression<bool>? canManageStock,
    Expression<bool>? canManageCategories,
    Expression<DateTime>? updatedAt,
    Expression<DateTime>? deletedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (uuid != null) 'uuid': uuid,
      if (username != null) 'username': username,
      if (fullName != null) 'full_name': fullName,
      if (role != null) 'role': role,
      if (isOwner != null) 'is_owner': isOwner,
      if (canViewProducts != null) 'can_view_products': canViewProducts,
      if (canAddProducts != null) 'can_add_products': canAddProducts,
      if (canEditProducts != null) 'can_edit_products': canEditProducts,
      if (canDeleteProducts != null) 'can_delete_products': canDeleteProducts,
      if (canManageStock != null) 'can_manage_stock': canManageStock,
      if (canManageCategories != null)
        'can_manage_categories': canManageCategories,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (deletedAt != null) 'deleted_at': deletedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  MembershipsCompanion copyWith({
    Value<String>? uuid,
    Value<String>? username,
    Value<String>? fullName,
    Value<String>? role,
    Value<bool>? isOwner,
    Value<bool>? canViewProducts,
    Value<bool>? canAddProducts,
    Value<bool>? canEditProducts,
    Value<bool>? canDeleteProducts,
    Value<bool>? canManageStock,
    Value<bool>? canManageCategories,
    Value<DateTime?>? updatedAt,
    Value<DateTime?>? deletedAt,
    Value<int>? rowid,
  }) {
    return MembershipsCompanion(
      uuid: uuid ?? this.uuid,
      username: username ?? this.username,
      fullName: fullName ?? this.fullName,
      role: role ?? this.role,
      isOwner: isOwner ?? this.isOwner,
      canViewProducts: canViewProducts ?? this.canViewProducts,
      canAddProducts: canAddProducts ?? this.canAddProducts,
      canEditProducts: canEditProducts ?? this.canEditProducts,
      canDeleteProducts: canDeleteProducts ?? this.canDeleteProducts,
      canManageStock: canManageStock ?? this.canManageStock,
      canManageCategories: canManageCategories ?? this.canManageCategories,
      updatedAt: updatedAt ?? this.updatedAt,
      deletedAt: deletedAt ?? this.deletedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (uuid.present) {
      map['uuid'] = Variable<String>(uuid.value);
    }
    if (username.present) {
      map['username'] = Variable<String>(username.value);
    }
    if (fullName.present) {
      map['full_name'] = Variable<String>(fullName.value);
    }
    if (role.present) {
      map['role'] = Variable<String>(role.value);
    }
    if (isOwner.present) {
      map['is_owner'] = Variable<bool>(isOwner.value);
    }
    if (canViewProducts.present) {
      map['can_view_products'] = Variable<bool>(canViewProducts.value);
    }
    if (canAddProducts.present) {
      map['can_add_products'] = Variable<bool>(canAddProducts.value);
    }
    if (canEditProducts.present) {
      map['can_edit_products'] = Variable<bool>(canEditProducts.value);
    }
    if (canDeleteProducts.present) {
      map['can_delete_products'] = Variable<bool>(canDeleteProducts.value);
    }
    if (canManageStock.present) {
      map['can_manage_stock'] = Variable<bool>(canManageStock.value);
    }
    if (canManageCategories.present) {
      map['can_manage_categories'] = Variable<bool>(canManageCategories.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (deletedAt.present) {
      map['deleted_at'] = Variable<DateTime>(deletedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('MembershipsCompanion(')
          ..write('uuid: $uuid, ')
          ..write('username: $username, ')
          ..write('fullName: $fullName, ')
          ..write('role: $role, ')
          ..write('isOwner: $isOwner, ')
          ..write('canViewProducts: $canViewProducts, ')
          ..write('canAddProducts: $canAddProducts, ')
          ..write('canEditProducts: $canEditProducts, ')
          ..write('canDeleteProducts: $canDeleteProducts, ')
          ..write('canManageStock: $canManageStock, ')
          ..write('canManageCategories: $canManageCategories, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('deletedAt: $deletedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $SyncMarksTable syncMarks = $SyncMarksTable(this);
  late final $OutboxTable outbox = $OutboxTable(this);
  late final $ShopsTable shops = $ShopsTable(this);
  late final $CategoriesTable categories = $CategoriesTable(this);
  late final $ProductsTable products = $ProductsTable(this);
  late final $MovementsTable movements = $MovementsTable(this);
  late final $NotificationsTable notifications = $NotificationsTable(this);
  late final $MembershipsTable memberships = $MembershipsTable(this);
  late final Index outboxOpId = Index(
    'outbox_op_id',
    'CREATE UNIQUE INDEX outbox_op_id ON outbox (op_id)',
  );
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
    syncMarks,
    outbox,
    shops,
    categories,
    products,
    movements,
    notifications,
    memberships,
    outboxOpId,
  ];
}

typedef $$SyncMarksTableCreateCompanionBuilder = SyncMarksCompanion Function({
  required String entity,
  Value<String> cursor,
  Value<DateTime?> syncedAt,
  Value<int> rowid,
});
typedef $$SyncMarksTableUpdateCompanionBuilder = SyncMarksCompanion Function({
  Value<String> entity,
  Value<String> cursor,
  Value<DateTime?> syncedAt,
  Value<int> rowid,
});

class $$SyncMarksTableFilterComposer
    extends Composer<_$AppDatabase, $SyncMarksTable> {
  $$SyncMarksTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get entity => $composableBuilder(
    column: $table.entity,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get cursor => $composableBuilder(
    column: $table.cursor,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get syncedAt => $composableBuilder(
    column: $table.syncedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$SyncMarksTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncMarksTable> {
  $$SyncMarksTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get entity => $composableBuilder(
    column: $table.entity,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get cursor => $composableBuilder(
    column: $table.cursor,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get syncedAt => $composableBuilder(
    column: $table.syncedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$SyncMarksTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncMarksTable> {
  $$SyncMarksTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get entity =>
      $composableBuilder(column: $table.entity, builder: (column) => column);

  GeneratedColumn<String> get cursor =>
      $composableBuilder(column: $table.cursor, builder: (column) => column);

  GeneratedColumn<DateTime> get syncedAt =>
      $composableBuilder(column: $table.syncedAt, builder: (column) => column);
}

class $$SyncMarksTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $SyncMarksTable,
          SyncMarkRow,
          $$SyncMarksTableFilterComposer,
          $$SyncMarksTableOrderingComposer,
          $$SyncMarksTableAnnotationComposer,
          $$SyncMarksTableCreateCompanionBuilder,
          $$SyncMarksTableUpdateCompanionBuilder,
          (
            SyncMarkRow,
            BaseReferences<_$AppDatabase, $SyncMarksTable, SyncMarkRow>,
          ),
          SyncMarkRow,
          PrefetchHooks Function()
        > {
  $$SyncMarksTableTableManager(_$AppDatabase db, $SyncMarksTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncMarksTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncMarksTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncMarksTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> entity = const Value.absent(),
                Value<String> cursor = const Value.absent(),
                Value<DateTime?> syncedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => SyncMarksCompanion(
                entity: entity,
                cursor: cursor,
                syncedAt: syncedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String entity,
                Value<String> cursor = const Value.absent(),
                Value<DateTime?> syncedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => SyncMarksCompanion.insert(
                entity: entity,
                cursor: cursor,
                syncedAt: syncedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$SyncMarksTable, SyncMarkRow>(table),
                  BaseReferences<_$AppDatabase, $SyncMarksTable, SyncMarkRow>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$SyncMarksTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $SyncMarksTable,
      SyncMarkRow,
      $$SyncMarksTableFilterComposer,
      $$SyncMarksTableOrderingComposer,
      $$SyncMarksTableAnnotationComposer,
      $$SyncMarksTableCreateCompanionBuilder,
      $$SyncMarksTableUpdateCompanionBuilder,
      (
        SyncMarkRow,
        BaseReferences<_$AppDatabase, $SyncMarksTable, SyncMarkRow>,
      ),
      SyncMarkRow,
      PrefetchHooks Function()
    >;
typedef $$OutboxTableCreateCompanionBuilder = OutboxCompanion Function({
  Value<int> seq,
  required String opId,
  required String entity,
  required String type,
  Value<String?> uuid,
  Value<String> payload,
  required DateTime clientTime,
  Value<String> deviceId,
  Value<String?> lastError,
  Value<String?> reasonCode,
  Value<int> attempts,
  Value<DateTime?> lastAttemptAt,
});
typedef $$OutboxTableUpdateCompanionBuilder = OutboxCompanion Function({
  Value<int> seq,
  Value<String> opId,
  Value<String> entity,
  Value<String> type,
  Value<String?> uuid,
  Value<String> payload,
  Value<DateTime> clientTime,
  Value<String> deviceId,
  Value<String?> lastError,
  Value<String?> reasonCode,
  Value<int> attempts,
  Value<DateTime?> lastAttemptAt,
});

class $$OutboxTableFilterComposer
    extends Composer<_$AppDatabase, $OutboxTable> {
  $$OutboxTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get seq => $composableBuilder(
    column: $table.seq,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get opId => $composableBuilder(
    column: $table.opId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get entity => $composableBuilder(
    column: $table.entity,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get type => $composableBuilder(
    column: $table.type,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payload => $composableBuilder(
    column: $table.payload,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get clientTime => $composableBuilder(
    column: $table.clientTime,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get deviceId => $composableBuilder(
    column: $table.deviceId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get lastError => $composableBuilder(
    column: $table.lastError,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get reasonCode => $composableBuilder(
    column: $table.reasonCode,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get attempts => $composableBuilder(
    column: $table.attempts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get lastAttemptAt => $composableBuilder(
    column: $table.lastAttemptAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$OutboxTableOrderingComposer
    extends Composer<_$AppDatabase, $OutboxTable> {
  $$OutboxTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get seq => $composableBuilder(
    column: $table.seq,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get opId => $composableBuilder(
    column: $table.opId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get entity => $composableBuilder(
    column: $table.entity,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get type => $composableBuilder(
    column: $table.type,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payload => $composableBuilder(
    column: $table.payload,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get clientTime => $composableBuilder(
    column: $table.clientTime,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get deviceId => $composableBuilder(
    column: $table.deviceId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get lastError => $composableBuilder(
    column: $table.lastError,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get reasonCode => $composableBuilder(
    column: $table.reasonCode,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get attempts => $composableBuilder(
    column: $table.attempts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get lastAttemptAt => $composableBuilder(
    column: $table.lastAttemptAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$OutboxTableAnnotationComposer
    extends Composer<_$AppDatabase, $OutboxTable> {
  $$OutboxTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get seq =>
      $composableBuilder(column: $table.seq, builder: (column) => column);

  GeneratedColumn<String> get opId =>
      $composableBuilder(column: $table.opId, builder: (column) => column);

  GeneratedColumn<String> get entity =>
      $composableBuilder(column: $table.entity, builder: (column) => column);

  GeneratedColumn<String> get type =>
      $composableBuilder(column: $table.type, builder: (column) => column);

  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<DateTime> get clientTime => $composableBuilder(
    column: $table.clientTime,
    builder: (column) => column,
  );

  GeneratedColumn<String> get deviceId =>
      $composableBuilder(column: $table.deviceId, builder: (column) => column);

  GeneratedColumn<String> get lastError =>
      $composableBuilder(column: $table.lastError, builder: (column) => column);

  GeneratedColumn<String> get reasonCode => $composableBuilder(
    column: $table.reasonCode,
    builder: (column) => column,
  );

  GeneratedColumn<int> get attempts =>
      $composableBuilder(column: $table.attempts, builder: (column) => column);

  GeneratedColumn<DateTime> get lastAttemptAt => $composableBuilder(
    column: $table.lastAttemptAt,
    builder: (column) => column,
  );
}

class $$OutboxTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $OutboxTable,
          OutboxRow,
          $$OutboxTableFilterComposer,
          $$OutboxTableOrderingComposer,
          $$OutboxTableAnnotationComposer,
          $$OutboxTableCreateCompanionBuilder,
          $$OutboxTableUpdateCompanionBuilder,
          (OutboxRow, BaseReferences<_$AppDatabase, $OutboxTable, OutboxRow>),
          OutboxRow,
          PrefetchHooks Function()
        > {
  $$OutboxTableTableManager(_$AppDatabase db, $OutboxTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$OutboxTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$OutboxTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$OutboxTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<int> seq = const Value.absent(),
                Value<String> opId = const Value.absent(),
                Value<String> entity = const Value.absent(),
                Value<String> type = const Value.absent(),
                Value<String?> uuid = const Value.absent(),
                Value<String> payload = const Value.absent(),
                Value<DateTime> clientTime = const Value.absent(),
                Value<String> deviceId = const Value.absent(),
                Value<String?> lastError = const Value.absent(),
                Value<String?> reasonCode = const Value.absent(),
                Value<int> attempts = const Value.absent(),
                Value<DateTime?> lastAttemptAt = const Value.absent(),
              }) => OutboxCompanion(
                seq: seq,
                opId: opId,
                entity: entity,
                type: type,
                uuid: uuid,
                payload: payload,
                clientTime: clientTime,
                deviceId: deviceId,
                lastError: lastError,
                reasonCode: reasonCode,
                attempts: attempts,
                lastAttemptAt: lastAttemptAt,
              ),
          createCompanionCallback:
              ({
                Value<int> seq = const Value.absent(),
                required String opId,
                required String entity,
                required String type,
                Value<String?> uuid = const Value.absent(),
                Value<String> payload = const Value.absent(),
                required DateTime clientTime,
                Value<String> deviceId = const Value.absent(),
                Value<String?> lastError = const Value.absent(),
                Value<String?> reasonCode = const Value.absent(),
                Value<int> attempts = const Value.absent(),
                Value<DateTime?> lastAttemptAt = const Value.absent(),
              }) => OutboxCompanion.insert(
                seq: seq,
                opId: opId,
                entity: entity,
                type: type,
                uuid: uuid,
                payload: payload,
                clientTime: clientTime,
                deviceId: deviceId,
                lastError: lastError,
                reasonCode: reasonCode,
                attempts: attempts,
                lastAttemptAt: lastAttemptAt,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$OutboxTable, OutboxRow>(table),
                  BaseReferences<_$AppDatabase, $OutboxTable, OutboxRow>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$OutboxTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $OutboxTable,
      OutboxRow,
      $$OutboxTableFilterComposer,
      $$OutboxTableOrderingComposer,
      $$OutboxTableAnnotationComposer,
      $$OutboxTableCreateCompanionBuilder,
      $$OutboxTableUpdateCompanionBuilder,
      (OutboxRow, BaseReferences<_$AppDatabase, $OutboxTable, OutboxRow>),
      OutboxRow,
      PrefetchHooks Function()
    >;
typedef $$ShopsTableCreateCompanionBuilder = ShopsCompanion Function({
  required String uuid,
  required String name,
  Value<String> currency,
  Value<String> primaryColor,
  Value<String> sidebarColor,
  Value<String> headerColor,
  Value<String> backgroundColor,
  Value<bool> scannerEnabled,
  Value<bool> barcodeFieldEnabled,
  Value<String?> logoUrl,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});
typedef $$ShopsTableUpdateCompanionBuilder = ShopsCompanion Function({
  Value<String> uuid,
  Value<String> name,
  Value<String> currency,
  Value<String> primaryColor,
  Value<String> sidebarColor,
  Value<String> headerColor,
  Value<String> backgroundColor,
  Value<bool> scannerEnabled,
  Value<bool> barcodeFieldEnabled,
  Value<String?> logoUrl,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});

class $$ShopsTableFilterComposer extends Composer<_$AppDatabase, $ShopsTable> {
  $$ShopsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get currency => $composableBuilder(
    column: $table.currency,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get primaryColor => $composableBuilder(
    column: $table.primaryColor,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get sidebarColor => $composableBuilder(
    column: $table.sidebarColor,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get headerColor => $composableBuilder(
    column: $table.headerColor,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get backgroundColor => $composableBuilder(
    column: $table.backgroundColor,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get scannerEnabled => $composableBuilder(
    column: $table.scannerEnabled,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get barcodeFieldEnabled => $composableBuilder(
    column: $table.barcodeFieldEnabled,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get logoUrl => $composableBuilder(
    column: $table.logoUrl,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$ShopsTableOrderingComposer
    extends Composer<_$AppDatabase, $ShopsTable> {
  $$ShopsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get currency => $composableBuilder(
    column: $table.currency,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get primaryColor => $composableBuilder(
    column: $table.primaryColor,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get sidebarColor => $composableBuilder(
    column: $table.sidebarColor,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get headerColor => $composableBuilder(
    column: $table.headerColor,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get backgroundColor => $composableBuilder(
    column: $table.backgroundColor,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get scannerEnabled => $composableBuilder(
    column: $table.scannerEnabled,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get barcodeFieldEnabled => $composableBuilder(
    column: $table.barcodeFieldEnabled,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get logoUrl => $composableBuilder(
    column: $table.logoUrl,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$ShopsTableAnnotationComposer
    extends Composer<_$AppDatabase, $ShopsTable> {
  $$ShopsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<String> get currency =>
      $composableBuilder(column: $table.currency, builder: (column) => column);

  GeneratedColumn<String> get primaryColor => $composableBuilder(
    column: $table.primaryColor,
    builder: (column) => column,
  );

  GeneratedColumn<String> get sidebarColor => $composableBuilder(
    column: $table.sidebarColor,
    builder: (column) => column,
  );

  GeneratedColumn<String> get headerColor => $composableBuilder(
    column: $table.headerColor,
    builder: (column) => column,
  );

  GeneratedColumn<String> get backgroundColor => $composableBuilder(
    column: $table.backgroundColor,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get scannerEnabled => $composableBuilder(
    column: $table.scannerEnabled,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get barcodeFieldEnabled => $composableBuilder(
    column: $table.barcodeFieldEnabled,
    builder: (column) => column,
  );

  GeneratedColumn<String> get logoUrl =>
      $composableBuilder(column: $table.logoUrl, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get deletedAt =>
      $composableBuilder(column: $table.deletedAt, builder: (column) => column);
}

class $$ShopsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $ShopsTable,
          ShopRow,
          $$ShopsTableFilterComposer,
          $$ShopsTableOrderingComposer,
          $$ShopsTableAnnotationComposer,
          $$ShopsTableCreateCompanionBuilder,
          $$ShopsTableUpdateCompanionBuilder,
          (ShopRow, BaseReferences<_$AppDatabase, $ShopsTable, ShopRow>),
          ShopRow,
          PrefetchHooks Function()
        > {
  $$ShopsTableTableManager(_$AppDatabase db, $ShopsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ShopsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ShopsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ShopsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> name = const Value.absent(),
                Value<String> currency = const Value.absent(),
                Value<String> primaryColor = const Value.absent(),
                Value<String> sidebarColor = const Value.absent(),
                Value<String> headerColor = const Value.absent(),
                Value<String> backgroundColor = const Value.absent(),
                Value<bool> scannerEnabled = const Value.absent(),
                Value<bool> barcodeFieldEnabled = const Value.absent(),
                Value<String?> logoUrl = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ShopsCompanion(
                uuid: uuid,
                name: name,
                currency: currency,
                primaryColor: primaryColor,
                sidebarColor: sidebarColor,
                headerColor: headerColor,
                backgroundColor: backgroundColor,
                scannerEnabled: scannerEnabled,
                barcodeFieldEnabled: barcodeFieldEnabled,
                logoUrl: logoUrl,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String name,
                Value<String> currency = const Value.absent(),
                Value<String> primaryColor = const Value.absent(),
                Value<String> sidebarColor = const Value.absent(),
                Value<String> headerColor = const Value.absent(),
                Value<String> backgroundColor = const Value.absent(),
                Value<bool> scannerEnabled = const Value.absent(),
                Value<bool> barcodeFieldEnabled = const Value.absent(),
                Value<String?> logoUrl = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ShopsCompanion.insert(
                uuid: uuid,
                name: name,
                currency: currency,
                primaryColor: primaryColor,
                sidebarColor: sidebarColor,
                headerColor: headerColor,
                backgroundColor: backgroundColor,
                scannerEnabled: scannerEnabled,
                barcodeFieldEnabled: barcodeFieldEnabled,
                logoUrl: logoUrl,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$ShopsTable, ShopRow>(table),
                  BaseReferences<_$AppDatabase, $ShopsTable, ShopRow>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$ShopsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $ShopsTable,
      ShopRow,
      $$ShopsTableFilterComposer,
      $$ShopsTableOrderingComposer,
      $$ShopsTableAnnotationComposer,
      $$ShopsTableCreateCompanionBuilder,
      $$ShopsTableUpdateCompanionBuilder,
      (ShopRow, BaseReferences<_$AppDatabase, $ShopsTable, ShopRow>),
      ShopRow,
      PrefetchHooks Function()
    >;
typedef $$CategoriesTableCreateCompanionBuilder = CategoriesCompanion Function({
  required String uuid,
  required String name,
  Value<int> productCount,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});
typedef $$CategoriesTableUpdateCompanionBuilder = CategoriesCompanion Function({
  Value<String> uuid,
  Value<String> name,
  Value<int> productCount,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});

class $$CategoriesTableFilterComposer
    extends Composer<_$AppDatabase, $CategoriesTable> {
  $$CategoriesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get productCount => $composableBuilder(
    column: $table.productCount,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$CategoriesTableOrderingComposer
    extends Composer<_$AppDatabase, $CategoriesTable> {
  $$CategoriesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get productCount => $composableBuilder(
    column: $table.productCount,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$CategoriesTableAnnotationComposer
    extends Composer<_$AppDatabase, $CategoriesTable> {
  $$CategoriesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<int> get productCount => $composableBuilder(
    column: $table.productCount,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get deletedAt =>
      $composableBuilder(column: $table.deletedAt, builder: (column) => column);
}

class $$CategoriesTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $CategoriesTable,
          CategoryRow,
          $$CategoriesTableFilterComposer,
          $$CategoriesTableOrderingComposer,
          $$CategoriesTableAnnotationComposer,
          $$CategoriesTableCreateCompanionBuilder,
          $$CategoriesTableUpdateCompanionBuilder,
          (
            CategoryRow,
            BaseReferences<_$AppDatabase, $CategoriesTable, CategoryRow>,
          ),
          CategoryRow,
          PrefetchHooks Function()
        > {
  $$CategoriesTableTableManager(_$AppDatabase db, $CategoriesTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CategoriesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CategoriesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CategoriesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> name = const Value.absent(),
                Value<int> productCount = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CategoriesCompanion(
                uuid: uuid,
                name: name,
                productCount: productCount,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String name,
                Value<int> productCount = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CategoriesCompanion.insert(
                uuid: uuid,
                name: name,
                productCount: productCount,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$CategoriesTable, CategoryRow>(table),
                  BaseReferences<_$AppDatabase, $CategoriesTable, CategoryRow>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$CategoriesTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $CategoriesTable,
      CategoryRow,
      $$CategoriesTableFilterComposer,
      $$CategoriesTableOrderingComposer,
      $$CategoriesTableAnnotationComposer,
      $$CategoriesTableCreateCompanionBuilder,
      $$CategoriesTableUpdateCompanionBuilder,
      (
        CategoryRow,
        BaseReferences<_$AppDatabase, $CategoriesTable, CategoryRow>,
      ),
      CategoryRow,
      PrefetchHooks Function()
    >;
typedef $$ProductsTableCreateCompanionBuilder = ProductsCompanion Function({
  required String uuid,
  required String name,
  Value<String> sku,
  Value<String> barcode,
  Value<String?> categoryUuid,
  Value<String> categoryName,
  Value<int> quantity,
  Value<int> alertThreshold,
  Value<String> salePrice,
  Value<String> costPrice,
  Value<String> currency,
  Value<String> description,
  Value<String> level,
  Value<bool> hasPendingOp,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});
typedef $$ProductsTableUpdateCompanionBuilder = ProductsCompanion Function({
  Value<String> uuid,
  Value<String> name,
  Value<String> sku,
  Value<String> barcode,
  Value<String?> categoryUuid,
  Value<String> categoryName,
  Value<int> quantity,
  Value<int> alertThreshold,
  Value<String> salePrice,
  Value<String> costPrice,
  Value<String> currency,
  Value<String> description,
  Value<String> level,
  Value<bool> hasPendingOp,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});

class $$ProductsTableFilterComposer
    extends Composer<_$AppDatabase, $ProductsTable> {
  $$ProductsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get sku => $composableBuilder(
    column: $table.sku,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get barcode => $composableBuilder(
    column: $table.barcode,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get categoryUuid => $composableBuilder(
    column: $table.categoryUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get categoryName => $composableBuilder(
    column: $table.categoryName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get quantity => $composableBuilder(
    column: $table.quantity,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get alertThreshold => $composableBuilder(
    column: $table.alertThreshold,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get salePrice => $composableBuilder(
    column: $table.salePrice,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get costPrice => $composableBuilder(
    column: $table.costPrice,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get currency => $composableBuilder(
    column: $table.currency,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get description => $composableBuilder(
    column: $table.description,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get level => $composableBuilder(
    column: $table.level,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$ProductsTableOrderingComposer
    extends Composer<_$AppDatabase, $ProductsTable> {
  $$ProductsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get name => $composableBuilder(
    column: $table.name,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get sku => $composableBuilder(
    column: $table.sku,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get barcode => $composableBuilder(
    column: $table.barcode,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get categoryUuid => $composableBuilder(
    column: $table.categoryUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get categoryName => $composableBuilder(
    column: $table.categoryName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get quantity => $composableBuilder(
    column: $table.quantity,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get alertThreshold => $composableBuilder(
    column: $table.alertThreshold,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get salePrice => $composableBuilder(
    column: $table.salePrice,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get costPrice => $composableBuilder(
    column: $table.costPrice,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get currency => $composableBuilder(
    column: $table.currency,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get description => $composableBuilder(
    column: $table.description,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get level => $composableBuilder(
    column: $table.level,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$ProductsTableAnnotationComposer
    extends Composer<_$AppDatabase, $ProductsTable> {
  $$ProductsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get name =>
      $composableBuilder(column: $table.name, builder: (column) => column);

  GeneratedColumn<String> get sku =>
      $composableBuilder(column: $table.sku, builder: (column) => column);

  GeneratedColumn<String> get barcode =>
      $composableBuilder(column: $table.barcode, builder: (column) => column);

  GeneratedColumn<String> get categoryUuid => $composableBuilder(
    column: $table.categoryUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get categoryName => $composableBuilder(
    column: $table.categoryName,
    builder: (column) => column,
  );

  GeneratedColumn<int> get quantity =>
      $composableBuilder(column: $table.quantity, builder: (column) => column);

  GeneratedColumn<int> get alertThreshold => $composableBuilder(
    column: $table.alertThreshold,
    builder: (column) => column,
  );

  GeneratedColumn<String> get salePrice =>
      $composableBuilder(column: $table.salePrice, builder: (column) => column);

  GeneratedColumn<String> get costPrice =>
      $composableBuilder(column: $table.costPrice, builder: (column) => column);

  GeneratedColumn<String> get currency =>
      $composableBuilder(column: $table.currency, builder: (column) => column);

  GeneratedColumn<String> get description => $composableBuilder(
    column: $table.description,
    builder: (column) => column,
  );

  GeneratedColumn<String> get level =>
      $composableBuilder(column: $table.level, builder: (column) => column);

  GeneratedColumn<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get deletedAt =>
      $composableBuilder(column: $table.deletedAt, builder: (column) => column);
}

class $$ProductsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $ProductsTable,
          ProductRow,
          $$ProductsTableFilterComposer,
          $$ProductsTableOrderingComposer,
          $$ProductsTableAnnotationComposer,
          $$ProductsTableCreateCompanionBuilder,
          $$ProductsTableUpdateCompanionBuilder,
          (
            ProductRow,
            BaseReferences<_$AppDatabase, $ProductsTable, ProductRow>,
          ),
          ProductRow,
          PrefetchHooks Function()
        > {
  $$ProductsTableTableManager(_$AppDatabase db, $ProductsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ProductsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ProductsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ProductsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> name = const Value.absent(),
                Value<String> sku = const Value.absent(),
                Value<String> barcode = const Value.absent(),
                Value<String?> categoryUuid = const Value.absent(),
                Value<String> categoryName = const Value.absent(),
                Value<int> quantity = const Value.absent(),
                Value<int> alertThreshold = const Value.absent(),
                Value<String> salePrice = const Value.absent(),
                Value<String> costPrice = const Value.absent(),
                Value<String> currency = const Value.absent(),
                Value<String> description = const Value.absent(),
                Value<String> level = const Value.absent(),
                Value<bool> hasPendingOp = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ProductsCompanion(
                uuid: uuid,
                name: name,
                sku: sku,
                barcode: barcode,
                categoryUuid: categoryUuid,
                categoryName: categoryName,
                quantity: quantity,
                alertThreshold: alertThreshold,
                salePrice: salePrice,
                costPrice: costPrice,
                currency: currency,
                description: description,
                level: level,
                hasPendingOp: hasPendingOp,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String name,
                Value<String> sku = const Value.absent(),
                Value<String> barcode = const Value.absent(),
                Value<String?> categoryUuid = const Value.absent(),
                Value<String> categoryName = const Value.absent(),
                Value<int> quantity = const Value.absent(),
                Value<int> alertThreshold = const Value.absent(),
                Value<String> salePrice = const Value.absent(),
                Value<String> costPrice = const Value.absent(),
                Value<String> currency = const Value.absent(),
                Value<String> description = const Value.absent(),
                Value<String> level = const Value.absent(),
                Value<bool> hasPendingOp = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => ProductsCompanion.insert(
                uuid: uuid,
                name: name,
                sku: sku,
                barcode: barcode,
                categoryUuid: categoryUuid,
                categoryName: categoryName,
                quantity: quantity,
                alertThreshold: alertThreshold,
                salePrice: salePrice,
                costPrice: costPrice,
                currency: currency,
                description: description,
                level: level,
                hasPendingOp: hasPendingOp,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$ProductsTable, ProductRow>(table),
                  BaseReferences<_$AppDatabase, $ProductsTable, ProductRow>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$ProductsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $ProductsTable,
      ProductRow,
      $$ProductsTableFilterComposer,
      $$ProductsTableOrderingComposer,
      $$ProductsTableAnnotationComposer,
      $$ProductsTableCreateCompanionBuilder,
      $$ProductsTableUpdateCompanionBuilder,
      (ProductRow, BaseReferences<_$AppDatabase, $ProductsTable, ProductRow>),
      ProductRow,
      PrefetchHooks Function()
    >;
typedef $$MovementsTableCreateCompanionBuilder = MovementsCompanion Function({
  required String uuid,
  required String productUuid,
  Value<String> productName,
  Value<String> productSku,
  required String kind,
  required int quantity,
  Value<String> note,
  Value<String> username,
  Value<bool> hasPendingOp,
  Value<DateTime?> createdAt,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});
typedef $$MovementsTableUpdateCompanionBuilder = MovementsCompanion Function({
  Value<String> uuid,
  Value<String> productUuid,
  Value<String> productName,
  Value<String> productSku,
  Value<String> kind,
  Value<int> quantity,
  Value<String> note,
  Value<String> username,
  Value<bool> hasPendingOp,
  Value<DateTime?> createdAt,
  Value<DateTime?> updatedAt,
  Value<DateTime?> deletedAt,
  Value<int> rowid,
});

class $$MovementsTableFilterComposer
    extends Composer<_$AppDatabase, $MovementsTable> {
  $$MovementsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get productUuid => $composableBuilder(
    column: $table.productUuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get productName => $composableBuilder(
    column: $table.productName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get productSku => $composableBuilder(
    column: $table.productSku,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get kind => $composableBuilder(
    column: $table.kind,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get quantity => $composableBuilder(
    column: $table.quantity,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get note => $composableBuilder(
    column: $table.note,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get username => $composableBuilder(
    column: $table.username,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$MovementsTableOrderingComposer
    extends Composer<_$AppDatabase, $MovementsTable> {
  $$MovementsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get productUuid => $composableBuilder(
    column: $table.productUuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get productName => $composableBuilder(
    column: $table.productName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get productSku => $composableBuilder(
    column: $table.productSku,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get kind => $composableBuilder(
    column: $table.kind,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get quantity => $composableBuilder(
    column: $table.quantity,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get note => $composableBuilder(
    column: $table.note,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get username => $composableBuilder(
    column: $table.username,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$MovementsTableAnnotationComposer
    extends Composer<_$AppDatabase, $MovementsTable> {
  $$MovementsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get productUuid => $composableBuilder(
    column: $table.productUuid,
    builder: (column) => column,
  );

  GeneratedColumn<String> get productName => $composableBuilder(
    column: $table.productName,
    builder: (column) => column,
  );

  GeneratedColumn<String> get productSku => $composableBuilder(
    column: $table.productSku,
    builder: (column) => column,
  );

  GeneratedColumn<String> get kind =>
      $composableBuilder(column: $table.kind, builder: (column) => column);

  GeneratedColumn<int> get quantity =>
      $composableBuilder(column: $table.quantity, builder: (column) => column);

  GeneratedColumn<String> get note =>
      $composableBuilder(column: $table.note, builder: (column) => column);

  GeneratedColumn<String> get username =>
      $composableBuilder(column: $table.username, builder: (column) => column);

  GeneratedColumn<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get deletedAt =>
      $composableBuilder(column: $table.deletedAt, builder: (column) => column);
}

class $$MovementsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $MovementsTable,
          MovementRow,
          $$MovementsTableFilterComposer,
          $$MovementsTableOrderingComposer,
          $$MovementsTableAnnotationComposer,
          $$MovementsTableCreateCompanionBuilder,
          $$MovementsTableUpdateCompanionBuilder,
          (
            MovementRow,
            BaseReferences<_$AppDatabase, $MovementsTable, MovementRow>,
          ),
          MovementRow,
          PrefetchHooks Function()
        > {
  $$MovementsTableTableManager(_$AppDatabase db, $MovementsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$MovementsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$MovementsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$MovementsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> productUuid = const Value.absent(),
                Value<String> productName = const Value.absent(),
                Value<String> productSku = const Value.absent(),
                Value<String> kind = const Value.absent(),
                Value<int> quantity = const Value.absent(),
                Value<String> note = const Value.absent(),
                Value<String> username = const Value.absent(),
                Value<bool> hasPendingOp = const Value.absent(),
                Value<DateTime?> createdAt = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => MovementsCompanion(
                uuid: uuid,
                productUuid: productUuid,
                productName: productName,
                productSku: productSku,
                kind: kind,
                quantity: quantity,
                note: note,
                username: username,
                hasPendingOp: hasPendingOp,
                createdAt: createdAt,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String productUuid,
                Value<String> productName = const Value.absent(),
                Value<String> productSku = const Value.absent(),
                required String kind,
                required int quantity,
                Value<String> note = const Value.absent(),
                Value<String> username = const Value.absent(),
                Value<bool> hasPendingOp = const Value.absent(),
                Value<DateTime?> createdAt = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => MovementsCompanion.insert(
                uuid: uuid,
                productUuid: productUuid,
                productName: productName,
                productSku: productSku,
                kind: kind,
                quantity: quantity,
                note: note,
                username: username,
                hasPendingOp: hasPendingOp,
                createdAt: createdAt,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$MovementsTable, MovementRow>(table),
                  BaseReferences<_$AppDatabase, $MovementsTable, MovementRow>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$MovementsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $MovementsTable,
      MovementRow,
      $$MovementsTableFilterComposer,
      $$MovementsTableOrderingComposer,
      $$MovementsTableAnnotationComposer,
      $$MovementsTableCreateCompanionBuilder,
      $$MovementsTableUpdateCompanionBuilder,
      (
        MovementRow,
        BaseReferences<_$AppDatabase, $MovementsTable, MovementRow>,
      ),
      MovementRow,
      PrefetchHooks Function()
    >;
typedef $$NotificationsTableCreateCompanionBuilder =
    NotificationsCompanion Function({
      required String uuid,
      Value<String> kind,
      Value<String> kindLabel,
      Value<String> message,
      Value<String?> productName,
      Value<int?> quantity,
      Value<int?> alertThreshold,
      Value<String?> level,
      Value<int?> tone,
      Value<bool> isRead,
      Value<bool> hasPendingOp,
      Value<DateTime?> createdAt,
      Value<DateTime?> updatedAt,
      Value<DateTime?> deletedAt,
      Value<int> rowid,
    });
typedef $$NotificationsTableUpdateCompanionBuilder =
    NotificationsCompanion Function({
      Value<String> uuid,
      Value<String> kind,
      Value<String> kindLabel,
      Value<String> message,
      Value<String?> productName,
      Value<int?> quantity,
      Value<int?> alertThreshold,
      Value<String?> level,
      Value<int?> tone,
      Value<bool> isRead,
      Value<bool> hasPendingOp,
      Value<DateTime?> createdAt,
      Value<DateTime?> updatedAt,
      Value<DateTime?> deletedAt,
      Value<int> rowid,
    });

class $$NotificationsTableFilterComposer
    extends Composer<_$AppDatabase, $NotificationsTable> {
  $$NotificationsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get kind => $composableBuilder(
    column: $table.kind,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get kindLabel => $composableBuilder(
    column: $table.kindLabel,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get message => $composableBuilder(
    column: $table.message,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get productName => $composableBuilder(
    column: $table.productName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get quantity => $composableBuilder(
    column: $table.quantity,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get alertThreshold => $composableBuilder(
    column: $table.alertThreshold,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get level => $composableBuilder(
    column: $table.level,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get tone => $composableBuilder(
    column: $table.tone,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get isRead => $composableBuilder(
    column: $table.isRead,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$NotificationsTableOrderingComposer
    extends Composer<_$AppDatabase, $NotificationsTable> {
  $$NotificationsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get kind => $composableBuilder(
    column: $table.kind,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get kindLabel => $composableBuilder(
    column: $table.kindLabel,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get message => $composableBuilder(
    column: $table.message,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get productName => $composableBuilder(
    column: $table.productName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get quantity => $composableBuilder(
    column: $table.quantity,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get alertThreshold => $composableBuilder(
    column: $table.alertThreshold,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get level => $composableBuilder(
    column: $table.level,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get tone => $composableBuilder(
    column: $table.tone,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get isRead => $composableBuilder(
    column: $table.isRead,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$NotificationsTableAnnotationComposer
    extends Composer<_$AppDatabase, $NotificationsTable> {
  $$NotificationsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get kind =>
      $composableBuilder(column: $table.kind, builder: (column) => column);

  GeneratedColumn<String> get kindLabel =>
      $composableBuilder(column: $table.kindLabel, builder: (column) => column);

  GeneratedColumn<String> get message =>
      $composableBuilder(column: $table.message, builder: (column) => column);

  GeneratedColumn<String> get productName => $composableBuilder(
    column: $table.productName,
    builder: (column) => column,
  );

  GeneratedColumn<int> get quantity =>
      $composableBuilder(column: $table.quantity, builder: (column) => column);

  GeneratedColumn<int> get alertThreshold => $composableBuilder(
    column: $table.alertThreshold,
    builder: (column) => column,
  );

  GeneratedColumn<String> get level =>
      $composableBuilder(column: $table.level, builder: (column) => column);

  GeneratedColumn<int> get tone =>
      $composableBuilder(column: $table.tone, builder: (column) => column);

  GeneratedColumn<bool> get isRead =>
      $composableBuilder(column: $table.isRead, builder: (column) => column);

  GeneratedColumn<bool> get hasPendingOp => $composableBuilder(
    column: $table.hasPendingOp,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get deletedAt =>
      $composableBuilder(column: $table.deletedAt, builder: (column) => column);
}

class $$NotificationsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $NotificationsTable,
          NotificationRow,
          $$NotificationsTableFilterComposer,
          $$NotificationsTableOrderingComposer,
          $$NotificationsTableAnnotationComposer,
          $$NotificationsTableCreateCompanionBuilder,
          $$NotificationsTableUpdateCompanionBuilder,
          (
            NotificationRow,
            BaseReferences<_$AppDatabase, $NotificationsTable, NotificationRow>,
          ),
          NotificationRow,
          PrefetchHooks Function()
        > {
  $$NotificationsTableTableManager(_$AppDatabase db, $NotificationsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$NotificationsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$NotificationsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$NotificationsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> kind = const Value.absent(),
                Value<String> kindLabel = const Value.absent(),
                Value<String> message = const Value.absent(),
                Value<String?> productName = const Value.absent(),
                Value<int?> quantity = const Value.absent(),
                Value<int?> alertThreshold = const Value.absent(),
                Value<String?> level = const Value.absent(),
                Value<int?> tone = const Value.absent(),
                Value<bool> isRead = const Value.absent(),
                Value<bool> hasPendingOp = const Value.absent(),
                Value<DateTime?> createdAt = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => NotificationsCompanion(
                uuid: uuid,
                kind: kind,
                kindLabel: kindLabel,
                message: message,
                productName: productName,
                quantity: quantity,
                alertThreshold: alertThreshold,
                level: level,
                tone: tone,
                isRead: isRead,
                hasPendingOp: hasPendingOp,
                createdAt: createdAt,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                Value<String> kind = const Value.absent(),
                Value<String> kindLabel = const Value.absent(),
                Value<String> message = const Value.absent(),
                Value<String?> productName = const Value.absent(),
                Value<int?> quantity = const Value.absent(),
                Value<int?> alertThreshold = const Value.absent(),
                Value<String?> level = const Value.absent(),
                Value<int?> tone = const Value.absent(),
                Value<bool> isRead = const Value.absent(),
                Value<bool> hasPendingOp = const Value.absent(),
                Value<DateTime?> createdAt = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => NotificationsCompanion.insert(
                uuid: uuid,
                kind: kind,
                kindLabel: kindLabel,
                message: message,
                productName: productName,
                quantity: quantity,
                alertThreshold: alertThreshold,
                level: level,
                tone: tone,
                isRead: isRead,
                hasPendingOp: hasPendingOp,
                createdAt: createdAt,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$NotificationsTable, NotificationRow>(table),
                  BaseReferences<
                    _$AppDatabase,
                    $NotificationsTable,
                    NotificationRow
                  >(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$NotificationsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $NotificationsTable,
      NotificationRow,
      $$NotificationsTableFilterComposer,
      $$NotificationsTableOrderingComposer,
      $$NotificationsTableAnnotationComposer,
      $$NotificationsTableCreateCompanionBuilder,
      $$NotificationsTableUpdateCompanionBuilder,
      (
        NotificationRow,
        BaseReferences<_$AppDatabase, $NotificationsTable, NotificationRow>,
      ),
      NotificationRow,
      PrefetchHooks Function()
    >;
typedef $$MembershipsTableCreateCompanionBuilder =
    MembershipsCompanion Function({
      required String uuid,
      required String username,
      Value<String> fullName,
      Value<String> role,
      Value<bool> isOwner,
      Value<bool> canViewProducts,
      Value<bool> canAddProducts,
      Value<bool> canEditProducts,
      Value<bool> canDeleteProducts,
      Value<bool> canManageStock,
      Value<bool> canManageCategories,
      Value<DateTime?> updatedAt,
      Value<DateTime?> deletedAt,
      Value<int> rowid,
    });
typedef $$MembershipsTableUpdateCompanionBuilder =
    MembershipsCompanion Function({
      Value<String> uuid,
      Value<String> username,
      Value<String> fullName,
      Value<String> role,
      Value<bool> isOwner,
      Value<bool> canViewProducts,
      Value<bool> canAddProducts,
      Value<bool> canEditProducts,
      Value<bool> canDeleteProducts,
      Value<bool> canManageStock,
      Value<bool> canManageCategories,
      Value<DateTime?> updatedAt,
      Value<DateTime?> deletedAt,
      Value<int> rowid,
    });

class $$MembershipsTableFilterComposer
    extends Composer<_$AppDatabase, $MembershipsTable> {
  $$MembershipsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get username => $composableBuilder(
    column: $table.username,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get fullName => $composableBuilder(
    column: $table.fullName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get role => $composableBuilder(
    column: $table.role,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get isOwner => $composableBuilder(
    column: $table.isOwner,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canViewProducts => $composableBuilder(
    column: $table.canViewProducts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canAddProducts => $composableBuilder(
    column: $table.canAddProducts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canEditProducts => $composableBuilder(
    column: $table.canEditProducts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canDeleteProducts => $composableBuilder(
    column: $table.canDeleteProducts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canManageStock => $composableBuilder(
    column: $table.canManageStock,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<bool> get canManageCategories => $composableBuilder(
    column: $table.canManageCategories,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$MembershipsTableOrderingComposer
    extends Composer<_$AppDatabase, $MembershipsTable> {
  $$MembershipsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get uuid => $composableBuilder(
    column: $table.uuid,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get username => $composableBuilder(
    column: $table.username,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get fullName => $composableBuilder(
    column: $table.fullName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get role => $composableBuilder(
    column: $table.role,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get isOwner => $composableBuilder(
    column: $table.isOwner,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canViewProducts => $composableBuilder(
    column: $table.canViewProducts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canAddProducts => $composableBuilder(
    column: $table.canAddProducts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canEditProducts => $composableBuilder(
    column: $table.canEditProducts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canDeleteProducts => $composableBuilder(
    column: $table.canDeleteProducts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canManageStock => $composableBuilder(
    column: $table.canManageStock,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<bool> get canManageCategories => $composableBuilder(
    column: $table.canManageCategories,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
    column: $table.updatedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get deletedAt => $composableBuilder(
    column: $table.deletedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$MembershipsTableAnnotationComposer
    extends Composer<_$AppDatabase, $MembershipsTable> {
  $$MembershipsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get uuid =>
      $composableBuilder(column: $table.uuid, builder: (column) => column);

  GeneratedColumn<String> get username =>
      $composableBuilder(column: $table.username, builder: (column) => column);

  GeneratedColumn<String> get fullName =>
      $composableBuilder(column: $table.fullName, builder: (column) => column);

  GeneratedColumn<String> get role =>
      $composableBuilder(column: $table.role, builder: (column) => column);

  GeneratedColumn<bool> get isOwner =>
      $composableBuilder(column: $table.isOwner, builder: (column) => column);

  GeneratedColumn<bool> get canViewProducts => $composableBuilder(
    column: $table.canViewProducts,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get canAddProducts => $composableBuilder(
    column: $table.canAddProducts,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get canEditProducts => $composableBuilder(
    column: $table.canEditProducts,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get canDeleteProducts => $composableBuilder(
    column: $table.canDeleteProducts,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get canManageStock => $composableBuilder(
    column: $table.canManageStock,
    builder: (column) => column,
  );

  GeneratedColumn<bool> get canManageCategories => $composableBuilder(
    column: $table.canManageCategories,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  GeneratedColumn<DateTime> get deletedAt =>
      $composableBuilder(column: $table.deletedAt, builder: (column) => column);
}

class $$MembershipsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $MembershipsTable,
          MembershipRow,
          $$MembershipsTableFilterComposer,
          $$MembershipsTableOrderingComposer,
          $$MembershipsTableAnnotationComposer,
          $$MembershipsTableCreateCompanionBuilder,
          $$MembershipsTableUpdateCompanionBuilder,
          (
            MembershipRow,
            BaseReferences<_$AppDatabase, $MembershipsTable, MembershipRow>,
          ),
          MembershipRow,
          PrefetchHooks Function()
        > {
  $$MembershipsTableTableManager(_$AppDatabase db, $MembershipsTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$MembershipsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$MembershipsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$MembershipsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> uuid = const Value.absent(),
                Value<String> username = const Value.absent(),
                Value<String> fullName = const Value.absent(),
                Value<String> role = const Value.absent(),
                Value<bool> isOwner = const Value.absent(),
                Value<bool> canViewProducts = const Value.absent(),
                Value<bool> canAddProducts = const Value.absent(),
                Value<bool> canEditProducts = const Value.absent(),
                Value<bool> canDeleteProducts = const Value.absent(),
                Value<bool> canManageStock = const Value.absent(),
                Value<bool> canManageCategories = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => MembershipsCompanion(
                uuid: uuid,
                username: username,
                fullName: fullName,
                role: role,
                isOwner: isOwner,
                canViewProducts: canViewProducts,
                canAddProducts: canAddProducts,
                canEditProducts: canEditProducts,
                canDeleteProducts: canDeleteProducts,
                canManageStock: canManageStock,
                canManageCategories: canManageCategories,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String uuid,
                required String username,
                Value<String> fullName = const Value.absent(),
                Value<String> role = const Value.absent(),
                Value<bool> isOwner = const Value.absent(),
                Value<bool> canViewProducts = const Value.absent(),
                Value<bool> canAddProducts = const Value.absent(),
                Value<bool> canEditProducts = const Value.absent(),
                Value<bool> canDeleteProducts = const Value.absent(),
                Value<bool> canManageStock = const Value.absent(),
                Value<bool> canManageCategories = const Value.absent(),
                Value<DateTime?> updatedAt = const Value.absent(),
                Value<DateTime?> deletedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => MembershipsCompanion.insert(
                uuid: uuid,
                username: username,
                fullName: fullName,
                role: role,
                isOwner: isOwner,
                canViewProducts: canViewProducts,
                canAddProducts: canAddProducts,
                canEditProducts: canEditProducts,
                canDeleteProducts: canDeleteProducts,
                canManageStock: canManageStock,
                canManageCategories: canManageCategories,
                updatedAt: updatedAt,
                deletedAt: deletedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$MembershipsTable, MembershipRow>(table),
                  BaseReferences<
                    _$AppDatabase,
                    $MembershipsTable,
                    MembershipRow
                  >(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$MembershipsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $MembershipsTable,
      MembershipRow,
      $$MembershipsTableFilterComposer,
      $$MembershipsTableOrderingComposer,
      $$MembershipsTableAnnotationComposer,
      $$MembershipsTableCreateCompanionBuilder,
      $$MembershipsTableUpdateCompanionBuilder,
      (
        MembershipRow,
        BaseReferences<_$AppDatabase, $MembershipsTable, MembershipRow>,
      ),
      MembershipRow,
      PrefetchHooks Function()
    >;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$SyncMarksTableTableManager get syncMarks =>
      $$SyncMarksTableTableManager(_db, _db.syncMarks);
  $$OutboxTableTableManager get outbox =>
      $$OutboxTableTableManager(_db, _db.outbox);
  $$ShopsTableTableManager get shops =>
      $$ShopsTableTableManager(_db, _db.shops);
  $$CategoriesTableTableManager get categories =>
      $$CategoriesTableTableManager(_db, _db.categories);
  $$ProductsTableTableManager get products =>
      $$ProductsTableTableManager(_db, _db.products);
  $$MovementsTableTableManager get movements =>
      $$MovementsTableTableManager(_db, _db.movements);
  $$NotificationsTableTableManager get notifications =>
      $$NotificationsTableTableManager(_db, _db.notifications);
  $$MembershipsTableTableManager get memberships =>
      $$MembershipsTableTableManager(_db, _db.memberships);
}
